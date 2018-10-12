from opengever.activity import notification_center
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class NotificationsGet(Service):
    """API endpoint to get all notifications for a particular user.

    GET /@notifications/peter.mueller HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(NotificationsGet, self).__init__(context, request)
        self.params = []
        self.center = notification_center()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@notifications as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, notification_id = self.read_params()

        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")

        return self.serialize(
            self.get_notification(userid, notification_id) if
            notification_id else self.get_user_notifications())

    def get_notification(self, userid, notification_id):
        notification = self.center.get_notification(notification_id)
        if not notification:
            raise NotFound

        if not notification.userid == userid:
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")

        return notification

    def get_user_notifications(self):
        return self.center.get_current_users_notifications()

    def serialize(self, notifications):
        url = api.portal.get().absolute_url()
        if isinstance(notifications, list):
            return [n.serialize(url) for n in notifications]
        else:
            return notifications.serialize(url)

    def read_params(self):
        if len(self.params) not in [1, 2]:
            raise BadRequest("Must supply user ID as URL and optional "
                             "the notification id as path parameter.")

        if len(self.params) == 2:
            return self.params

        return self.params[0], None


class NotificationPatch(Service):
    """API endpoint to set a specific notification for a particular user as read.

    PATCH /@notifications/peter.mueller/3617 HTTP/1.1

    Payload: {
        "read": true
    }
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(NotificationPatch, self).__init__(context, request)
        self.params = []
        self.center = notification_center()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@notifications as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, notification_id = self.read_params()

        mark_as_read = json_body(self.request).get('read', False)

        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")

        notification = self.get_notification(userid, notification_id)
        if mark_as_read:
            self.center.mark_notification_as_read(notification.notification_id)

        self.request.response.setStatus(204)

    def get_notification(self, userid, notification_id):
        notification = self.center.get_notification(notification_id)
        if not notification:
            raise NotFound

        if not notification.userid == userid:
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")

        return notification

    def read_params(self):
        if len(self.params) != 2:
            raise BadRequest("Must supply user ID and the notification id "
                             "as path parameter.")

        return self.params
