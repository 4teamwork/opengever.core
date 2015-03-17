from opengever.activity.interfaces import INotificationEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class NotificationEvent(ObjectEvent):

    implements(INotificationEvent)

    def __init__(self, obj, kind, summary, actor, description=u''):
        self.object = obj
        self.kind = kind
        self.summary = summary
        self.actor = actor
        self.description = description
