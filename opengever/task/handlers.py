from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from opengever.base.security import elevated_privileges
from opengever.document.behaviors import IBaseDocument
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.inbox.activities import ForwardingAddedActivity
from opengever.inbox.forwarding import IForwarding
from opengever.task import CLOSED_TO_IN_PROGRESS_TRANSITION
from opengever.task import FINAL_TRANSITIONS
from opengever.task.activities import TaskAddedActivity
from opengever.task.browser.transitioncontroller import TaskChecker
from opengever.task.localroles import LocalRolesSetter
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderTriggering
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest


def delete_copied_task(copied_task, event):
    """Prevent tasks from being copied.

    This deletes the task from the copied subtree (a ZEXP) before the subtree
    gets inserted into the destination location.

    Suppress deletion events in order to avoid attempts to uncatalog
    an object that
    1) hasn't even been cataloged yet
    2) doesn't have a proper AQ chain because it's parts of a subtree
       that only exists as a temporary ZEXP that hasn't been attached to
       a container yet
    """
    with elevated_privileges():
        container = aq_parent(copied_task)
        container._delObject(copied_task.id, suppress_events=True)


def create_subtask_response(context, event):
    """When adding a new task object within a task(subtask),
    it adds a response to the maintask.
    """

    # the event is fired multiple times when the task was transported, so we
    # need to verify that the request was not called by another client.
    request = context.REQUEST
    if request.get_header('X-OGDS-AC', None) or \
            request.get('X-CREATING-SUCCESSOR', None):
        return

    parent = aq_parent(aq_inner(context))
    if ITask.providedBy(parent):
        if ITask.providedBy(context):
            transition = 'transition-add-subtask'

            # If the the added object is a subtask we have to make sure
            # that the subtask is already synced to the globalindex
            if not context.get_sql_object():
                TaskSqlSyncer(context, event).sync()

        elif IBaseDocument.providedBy(context):
            transition = 'transition-add-document'

        # add a response with a link to the object
        add_simple_response(parent, added_objects=[context],
                            transition=transition)


def set_dates(task, event):
    """Set expectedStartOfWork and completion date, when a corresponding
    transition succeded."""

    resolved_transitions = ['task-transition-in-progress-resolved',
                            'task-transition-open-resolved',
                            'task-transition-open-tested-and-closed',
                            'task-transition-in-progress-tested-and-closed',
                            ]

    if event.action == 'task-transition-open-in-progress':
        task.expectedStartOfWork = date.today()
    elif event.action in resolved_transitions:
        task.date_of_completion = date.today()
    if event.action == 'task-transition-resolved-in-progress':
        task.date_of_completion = None


def cancel_subtasks(task, event):
    if event.action not in ['task-transition-in-progress-cancelled',
                            'task-transition-open-cancelled']:

        return

    task.cancel_subtasks()


def review_state_changed(task, event):
    if not task.is_from_tasktemplate or not task.get_is_subtask():
        return

    if event.action in FINAL_TRANSITIONS:
        task.sync()
        if TaskChecker(task.aq_parent.get_sql_object()).all_subtasks_finished:
            task.close_main_task()
            return

    if event.action not in ['task-transition-open-resolved',
                            'task-transition-open-tested-and-closed',
                            'task-transition-in-progress-resolved',
                            'task-transition-in-progress-tested-and-closed',
                            'task-transition-rejected-skipped']:
        return

    if task.is_part_of_sequential_process:
        task.open_next_task()

        # We need to know later on the after_transition_hook of the task
        # transition extender if this review state change opened a next task.
        task._v_transition_opened_next_task = True


def set_initial_state(task, event):
    """When adding a subtask to a sequential task process, the new task should
    be in the planned state.
    """
    if IDuringTaskTemplateFolderTriggering.providedBy(getRequest()):
        return

    parent = aq_parent(aq_inner(task))
    if ITask.providedBy(parent) \
       and parent.is_sequential_main_task():

        task.set_to_planned_state()


def revoke_permissions(task, event):
    """Revoke temporary local roles on task and its related objects,
    except if revoke_permissions is set to False
    """
    if event.action in FINAL_TRANSITIONS and task.revoke_permissions:
        return LocalRolesSetter(task).revoke_roles()


def set_roles_after_adding(context, event):
    LocalRolesSetter(context).set_roles(event)


def set_roles_after_modifying(context, event):
    # Handle the modify event having been a removal of a related item
    setattr(
        context,
        'relatedItems',
        [item for item in getattr(context, 'relatedItems', []) if item.to_object],
    )

    if IContainerModifiedEvent.providedBy(event):
        return

    LocalRolesSetter(context).set_roles(event)


def set_roles_when_reopen_a_closed_task(context, event):
    """Event handler which makes sure, the local roles are reassigned,
    after these have been revoked at the closing of the task.
    """
    if event.action in CLOSED_TO_IN_PROGRESS_TRANSITION:
        LocalRolesSetter(context).set_roles(event)


def record_added_activity(task, event):
    """Record task added activity, which also sets watchers and
    creates notifications.
    """
    # Skip tasks created during successor creation, those are handled manually
    if getRequest().get('X-CREATING-SUCCESSOR', None):
        return

    # Skip tasks created during tasktemplatefolder triggering, those are
    # handled manually
    if IDuringTaskTemplateFolderTriggering.providedBy(getRequest()):
        return

    if IForwarding.providedBy(task):
        activity = ForwardingAddedActivity(task, getRequest())
    else:
        activity = TaskAddedActivity(task, getRequest())

    activity.record()
