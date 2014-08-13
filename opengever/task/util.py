from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.task import _
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl
import opengever.task
import types


CUSTOM_INITIAL_VERSION_MESSAGE = 'custom_inital_version_message'
TASK_TYPE_CATEGORIES = ['unidirectional_by_reference',
                        'unidirectional_by_value',
                        'bidirectional_by_reference',
                        'bidirectional_by_value']


class UsersVocabulary(SimpleVocabulary):

    def search(self, query_string):
        return [v for v in self if query_string.lower() in v.value.lower()]


@grok.provider(IContextSourceBinder)
def getTransitionVocab(context):

    if AccessControl.getSecurityManager(
        ).getUser() == AccessControl.SpecialUsers.nobody:
        return SimpleVocabulary([])

    wftool = getToolByName(context, 'portal_workflow')
    transitions = []
    if opengever.task.task.ITask.providedBy(context) and \
            context.REQUEST.URL.find('++add++opengever.task.task') == -1:
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(SimpleVocabulary.createTerm(
                    tdef['id'],
                    tdef['id'],
                    PMF(tdef['id'], default=tdef['title_or_id'])))
        return SimpleVocabulary(transitions)

    else:
        wf = wftool.get(wftool.getChainForPortalType('opengever.task.task')[0])
        state = wf.states.get(wf.initial_state)
        for tid in state.transitions:
            tdef = wf.transitions.get(tid, None)
            transitions.append(SimpleVocabulary.createTerm(
                    tdef.id,
                    tdef.id,
                    PMF(tdef.id, default=tdef.title_or_id)))
        return SimpleVocabulary(transitions)


@grok.provider(IContextSourceBinder)
def getTaskTypeVocabulary(context):
    terms = []
    for category in TASK_TYPE_CATEGORIES:
        reg_key = 'opengever.task.interfaces.ITaskSettings.%s' % (
            category)

        for term in wrap_vocabulary(
            'opengever.task.%s' % (category),
            visible_terms_from_registry=reg_key)(context):

            terms.append(term)

    return SimpleVocabulary(terms)


def get_task_type_title(task_type, language):
    """Return the task type translated in language.

    """
    for category in TASK_TYPE_CATEGORIES:
        vocabulary_id = 'opengever.task.{}'.format(category)
        factory = getUtility(IVocabularyFactory, vocabulary_id)
        vdex_terms = factory.getTerms(language)
        for vdex_term in vdex_terms:
            if vdex_term['key'] == task_type:
                return vdex_term['value']


def add_simple_response(task, text='', field_changes=None, added_object=None,
                        successor_oguid=None, **kwargs):
    """Add a simple response which does (not change the task itself).
    `task`: task context
    `text`: fulltext
    `added_object`: an object which was added to the task
    `successor_oguid`: an OGUID to a (remote) object which was referenced.
    """

    response = opengever.task.adapters.Response(text)
    response.type = 'additional'

    for key, value in kwargs.items():
        setattr(response, key, value)

    if field_changes:
        for field, new_value in field_changes:
            old_value = field.get(field.interface(task))
            if old_value != new_value:
                response.add_change(
                    field.__name__,
                    field.title,
                    old_value,
                    new_value)

    if added_object:
        intids = getUtility(IIntIds)

        if isinstance(added_object, types.ListType) or \
                isinstance(added_object, types.TupleType) or \
                isinstance(added_object, types.GeneratorType):
            response.added_object = PersistentList()
            for obj in added_object:
                iid = intids.getId(obj)
                response.added_object.append(RelationValue(iid))

        else:
            iid = intids.getId(added_object)
            response.added_object = RelationValue(iid)

    if successor_oguid:
        response.successor_oguid = successor_oguid

    container = opengever.task.adapters.IResponseContainer(task)
    container.add(response)

    notify(ObjectModifiedEvent(task))

    return response


def change_task_workflow_state(task, transition, **kwargs):
    """Changes the workflow state of the task by executing a transition
    and adding a response. The keyword args are passed to
    add_simple_response, allowing to add additional information on the
    created response.
    """

    wftool = getToolByName(task, 'portal_workflow')

    before = wftool.getInfoFor(task, 'review_state')
    before = wftool.getTitleForStateOnType(before, task.Type())

    wftool.doActionFor(task, transition)

    after = wftool.getInfoFor(task, 'review_state')
    after = wftool.getTitleForStateOnType(after, task.Type())

    response = add_simple_response(task, **kwargs)
    response.add_change('review_state', _(u'Issue state'),
                        before, after)
    response.transition = transition
    return response


def get_documents_of_task(task, include_mails=False):
    """Returns all related and contained documents and mails for this task
    recursively as full object.
    """

    documents = []
    portal_types = ['opengever.document.document']
    if include_mails:
        portal_types.append('ftw.mail.mail')
    catalog = getToolByName(task, 'portal_catalog')
    membership = getToolByName(task, 'portal_membership')

    # Find documents within the task. There may also be subtasks containing
    # documents.
    query = {'path': '/'.join(task.getPhysicalPath()),
             'portal_type': portal_types}
    for doc in catalog(query):
        documents.append(doc.getObject())

    # Find referenced documents.
    for relation in getattr(task, 'relatedItems', []):
        doc = relation.to_object
        if doc.portal_type in portal_types and \
                membership.checkPermission('View', doc):
            documents.append(doc)

    return documents


class CustomInitialVersionMessage(object):
    """Context Manager for Cutom inital version message of a document.
    see create_initial_version handler in opengever.document"""

    def __init__(self, message, request):
        self.message = message
        self.request = request

    def __enter__(self):
        self.request.set(CUSTOM_INITIAL_VERSION_MESSAGE, self.message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.request[CUSTOM_INITIAL_VERSION_MESSAGE] = None
