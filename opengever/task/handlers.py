from Acquisition import aq_inner, aq_parent
from Products.CMFCore.interfaces import IActionSucceededEvent
from datetime import datetime
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
            request.get_header('X-OGDS-AUID', None) or \
            request.get('X-CREATING-SUCCESSOR', None):
        return

    parent = aq_parent(aq_inner(context))

    if ITask.providedBy(parent):
        # add a response with a link to the object
        add_simple_response(parent, added_object=context)


@grok.subscribe(ITask, IActionSucceededEvent)
def set_dates(task, event):
    """Set expectedStartOfWork and completion date, when a corresponding
    transition succeded."""

    resolved_transitions = ['task-transition-in-progress-resolved',
                            'task-transition-open-resolved',
                            'task-transition-open-tested-and-closed',
                            'task-transition-in-progress-tested-and-closed',
                            ]

    if event.action == 'task-transition-open-in-progress':
        task.expectedStartOfWork = datetime.now()
    elif event.action in resolved_transitions:
        task.date_of_completion = datetime.now()
    if event.action == 'task-transition-resolved-in-progress':
        task.date_of_completion = None
