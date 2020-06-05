from opengever.activity import is_activity_feature_enabled
from opengever.activity import notification_center
from opengever.inbox.activities import ForwardingWatcherAddedActivity
from opengever.inbox.forwarding import IForwarding
from opengever.task.activities import TaskWatcherAddedActivity
from opengever.task.task import ITask
from zope.globalrequest import getRequest


def log_activity(task, event):

    if not is_activity_feature_enabled():
        return

    notification_center().add_activity(
        event.object,
        event.kind,
        event.object.title,
        event.label,
        event.summary,
        event.actor.getId(),
        description=event.description)


def notify_watcher(obj, event):
    if IForwarding.providedBy(obj):
        activity = ForwardingWatcherAddedActivity(obj, getRequest(), event.watcherid)
    elif ITask.providedBy(obj):
        activity = TaskWatcherAddedActivity(obj, getRequest(), event.watcherid)
    activity.record()
