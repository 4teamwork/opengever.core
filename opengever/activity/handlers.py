from five import grok
from opengever.activity.interfaces import INotificationEvent
from opengever.activity.utils import notification_center
from opengever.task.task import ITask


@grok.subscribe(ITask, INotificationEvent)
def set_dates(task, event):
    notification_center().add_activity(
        event.object,
        event.kind,
        event.object.title,
        event.summary,
        event.actor.getId(),
        description=event.description)
