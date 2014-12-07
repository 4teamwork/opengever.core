from five import grok
from opengever.activity.interfaces import INotificationEvent
from opengever.activity.utils import notification_center
from opengever.globalindex.oguid import Oguid
from opengever.task.task import ITask


@grok.subscribe(ITask, INotificationEvent)
def set_dates(task, event):
    notification_center().add_acitivity(
        Oguid.for_object(event.object),
        event.kind,
        event.title,
        event.actor.getId(),
        description=event.description)
