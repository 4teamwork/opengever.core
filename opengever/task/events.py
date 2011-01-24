from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.task.behaviors import ITransitionMarker
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.dexterity.interfaces import IDexterityContent
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent


@grok.subscribe(ITransitionMarker, IObjectAddedEvent)
def do_transition(context, event):
    """ event handler for do a transition while crating a opengever.task object
    """
    annotations = IAnnotations(context.REQUEST)
    value = annotations.get('opengever.task.task')
    if value:
        wftool = getToolByName(context, 'portal_workflow')
        wftool.doActionFor(context, value)


@grok.subscribe(IDexterityContent, IObjectAddedEvent)
def create_response(context, event):
    """When adding a new task object within a task, add a response.
    """
    if context.REQUEST.get('X-CREATING-SUCCESSOR', None):
        return

    parent = aq_parent(aq_inner(context))

    tool = getToolByName(context, "portal_workflow")
    parent_review_state = tool.getInfoFor(aq_inner(context),
                                          'review_state', None)

    if ITask.providedBy(parent) and \
            parent_review_state != 'task-state-new-successor':
        # add a response with a link to the object
        add_simple_response(parent, added_object=context)
