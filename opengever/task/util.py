from collective.elephantvocabulary import wrap_vocabulary
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.team import Team
from opengever.task.activities import TaskTransitionActivity
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl
import opengever.task


CUSTOM_INITIAL_VERSION_MESSAGE = 'custom_inital_version_message'
TASK_TYPE_CATEGORIES = ['unidirectional_by_reference',
                        'unidirectional_by_value',
                        'bidirectional_by_reference',
                        'bidirectional_by_value']


class UsersVocabulary(SimpleVocabulary):

    def search(self, query_string):
        return [v for v in self if query_string.lower() in v.value.lower()]


@provider(IContextSourceBinder)
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


@provider(IContextSourceBinder)
def getTaskTypeVocabulary(context):
    terms = []
    for category in TASK_TYPE_CATEGORIES:
        reg_key = 'opengever.task.interfaces.ITaskSettings.%s' % (
            category)

        key = 'opengever.task.%s' % (category)
        for term in wrap_vocabulary(
                key, visible_terms_from_registry=reg_key)(context):

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


def add_simple_response(task, text='', field_changes=None, added_objects=None,
                        successor_oguid=None, supress_events=False,
                        supress_activity=False, **kwargs):
    """Add a simple response which does (not change the task itself).
    `task`: task context
    `text`: fulltext
    `added_objects`: objects which were added to the task
    `successor_oguid`: an OGUID to a (remote) object which was referenced.
    """

    response = Response()
    response.text = text

    for key, value in kwargs.items():
        setattr(response, key, value)

    if field_changes:
        for field, new_value in field_changes:
            old_value = field.get(field.interface(task))
            if old_value != new_value:
                response.add_change(
                    field.__name__,
                    old_value,
                    new_value,
                    field_title=field.title)

    if added_objects:
        intids = getUtility(IIntIds)
        for obj in added_objects:
            iid = intids.getId(obj)
            response.added_objects.append(RelationValue(iid))

    if successor_oguid:
        response.successor_oguid = successor_oguid

    container = IResponseContainer(task)
    container.add(response)

    if not supress_events:
        notify(ObjectModifiedEvent(task))

    if not supress_activity:
        TaskTransitionActivity(task, task.REQUEST, response).record()

    return response


def change_task_workflow_state(task, transition, disable_sync=False, **kwargs):
    """Changes the workflow state of the task.
    """

    wftool = api.portal.get_tool('portal_workflow')
    wftool.doActionFor(
        task, transition, disable_sync=disable_sync, transition_params=kwargs)


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


def update_reponsible_field_data(data):
    """The responsible field always contains the orgunit id and the userid
    separated by a colon.
    """
    if not data['responsible']:
        return

    if ActorLookup(data['responsible']).is_inbox():
        client = data['responsible'].split(':', 1)[1]
        data['responsible_client'] = client
        data['responsible'] = data['responsible']

    elif ActorLookup(data['responsible']).is_team():
        team = Team.query.get_by_actor_id(data['responsible'])
        data['responsible_client'] = team.org_unit.unit_id
        data['responsible'] = data['responsible']

    else:
        client, user = data['responsible'].split(':', 1)
        data['responsible_client'] = client
        data['responsible'] = user
