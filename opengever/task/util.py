from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl
import opengever.task


class UsersVocabulary(SimpleVocabulary):

    def search(self, query_string):
        return [v for v in self if query_string.lower() in v.value.lower()]


@grok.provider(IContextSourceBinder)
def getTransitionVocab(context):
    if AccessControl.getSecurityManager().getUser() == AccessControl.SpecialUsers.nobody:
        return SimpleVocabulary([])
    wftool = getToolByName(context, 'portal_workflow')
    transitions = []
    if opengever.task.task.ITask.providedBy(context) and context.REQUEST.URL.find('++add++opengever.task.task') == -1:
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(SimpleVocabulary.createTerm(tdef['id'],
                                                           tdef['id'],
                                                           PMF(tdef['id'],
                                                               default=tdef['title_or_id'])))
        return SimpleVocabulary(transitions)
    else:
        wf = wftool.get(wftool.getChainForPortalType('opengever.task.task')[0])
        state = wf.states.get(wf.initial_state)
        for tid in state.transitions:
            tdef= wf.transitions.get(tid, None)
            transitions.append(SimpleVocabulary.createTerm(tdef.id,
                                                           tdef.id,
                                                           PMF(tdef.id, default=tdef.title_or_id)))
        return SimpleVocabulary(transitions)


def create_sequence_number(obj, key='task_sequence_number'):
    portal = obj.portal_url.getPortalObject()
    portal_annotations = IAnnotations(portal)
    sequence_number = int(portal_annotations.get(key, 0)) + 1
    portal_annotations[key] = sequence_number
    return sequence_number


@grok.provider(IContextSourceBinder)
def getTaskTypeVocabulary(context):
    terms = []
    for task_type in ['unidirectional_by_reference',
                      'unidirectional_by_value',
                      'bidirectional_by_reference',
                      'bidirectional_by_value']:
        for term in wrap_vocabulary('opengever.task.'+task_type,
                                    visible_terms_from_registry=\
                                        'opengever.task.interfaces.ITaskSettings.' + \
                                        task_type)(context):
                                    terms.append(term)
    return SimpleVocabulary(terms)


def add_simple_response(task, text='', field_changes=None, added_object=None,
                        successor_oguid=None, **kwargs):
    """Add a simple response which does (not change the task itself).
    `task`: task context
    `text`: fulltext
    `added_object`: an object which was added to the task
    `successor_oguid`: an OGUID to a (remote) object which was referened.
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

        if hasattr(added_object, '__iter__'):
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
