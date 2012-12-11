from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.dexterity.interfaces import IDexterityContent
from zope.app.container.interfaces import IObjectAddedEvent


@grok.subscribe(IDexterityContent, IObjectAddedEvent)
def create_subtask_response(context, event):
    """When adding a new task object within a task(subtask),
    it adds a response to the maintask.
    """

    # the event is fired multiple times when the task was transported, so we
    # need to verify that the request was not called by another client.
    request = context.REQUEST
    if request.get_header('X-OGDS-AC', None) or \
            request.get_header('X-OGDS-CID', None) or \
            request.get('X-CREATING-SUCCESSOR', None):
        return

    parent = aq_parent(aq_inner(context))

    if ITask.providedBy(parent):
        # add a response with a link to the object
        add_simple_response(parent, added_object=context)
