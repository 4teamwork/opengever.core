from Acquisition import aq_inner, aq_parent
from datetime import date
from opengever.activity import notification_center
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.document.behaviors import IBaseDocument
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.task import _
from opengever.task import FINAL_TRANSITIONS
from opengever.task.adapters import IResponseContainer
from opengever.task.localroles import LocalRolesSetter
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderTriggering
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from plone import api
from zope.globalrequest import getRequest


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
        if ITask.providedBy(context):
            transition = 'transition-add-subtask'

            # If the the added object is a subtask we have to make sure
            # that the subtask is already synced to the globalindex
            if not context.get_sql_object():
                TaskSqlSyncer(context, event).sync()

        elif IBaseDocument.providedBy(context):
            transition = 'transition-add-document'

        # add a response with a link to the object
        add_simple_response(parent, added_object=context,
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


def reassign_team_tasks(task, event):
    if event.action != 'task-transition-open-in-progress':
        return

    if task.is_team_task:
        old_responsible = ITask(task).responsible
        ITask(task).responsible = api.user.get_current().getId()
        IResponseContainer(task)[-1].add_change(
            'responsible',
            _(u"label_responsible", default=u"Responsible"),
            old_responsible, ITask(task).responsible)


def set_responsible_to_issuer_on_reject(task, event):
    if event.action == 'task-transition-open-rejected':
        notification_center().remove_watcher_from_resource(task.oguid, task.responsible, TASK_RESPONSIBLE_ROLE)
        notification_center().add_watcher_to_resource(task.oguid, task.issuer, TASK_ISSUER_ROLE)
        notification_center().add_watcher_to_resource(task.oguid, task.issuer, TASK_RESPONSIBLE_ROLE)
        old_responsible = ITask(task).responsible
        task.responsible = task.issuer
        IResponseContainer(task)[-1].add_change(
            'responsible',
            _(u"label_responsible", default=u"Responsible"),
            old_responsible, ITask(task).responsible)


def cancel_subtasks(task, event):
    if event.action not in ['task-transition-in-progress-cancelled',
                            'task-transition-open-cancelled']:

        return

    task.cancel_subtasks()


def start_next_task(task, event):
    # todo also handle skipped tasks
    if event.action not in ['task-transition-open-resolved',
                            'task-transition-in-progress-resolved',
                            'task-transition-in-progress-tested-and-closed',
                            'task-transition-rejected-skipped',
                            'task-transition-planned-skipped']:
        return

    if task.is_from_sequential_tasktemplate:
        task.open_next_task()


def set_initial_state(task, event):
    """When adding a subtask to a sequential task process, the new task should
    be in the planned state.
    """
    if IDuringTaskTemplateFolderTriggering.providedBy(getRequest()):
        return

    parent = aq_parent(aq_inner(task))
    if ITask.providedBy(parent) \
       and IFromSequentialTasktemplate.providedBy(parent):

        task.set_to_planned_state()


def revoke_permissions(task, event):
    """Revoke temporary local roles on task and its related objects.
    """
    if event.action in FINAL_TRANSITIONS:
        return LocalRolesSetter(task).revoke_roles()
