from five import grok
from opengever.activity import is_activity_feature_enabled
from opengever.activity import notification_center
from opengever.activity.interfaces import INotificationEvent
from zope.interface import Interface


@grok.subscribe(Interface, INotificationEvent)
def log_activity(task, event):
    if is_activity_feature_enabled():
        notification_center().add_activity(
            event.object,
            event.kind,
            event.object.title,
            event.summary,
            event.actor.getId(),
            description=event.description)
