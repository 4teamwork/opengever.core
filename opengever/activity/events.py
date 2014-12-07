from opengever.activity.interfaces import INotificationEvent
from opengever.task.response_description import ResponseDescription
from plone import api
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class NotificationEvent(ObjectEvent):

    implements(INotificationEvent)

    def __init__(self, object, kind, title, actor, description=u''):
        self.object = object
        self.kind = kind
        self.title = title
        self.actor = actor
        self.description = description


class TaskNotifactionEvent(NotificationEvent):

    def __init__(self, object, response, actor=None):
        self.object = object
        self.kind = response.transition
        self.title = ResponseDescription.get(response=response).msg()
        self.description = response.text

        if actor:
            self.actor = actor
        else:
            self.actor = api.user.get_current()
