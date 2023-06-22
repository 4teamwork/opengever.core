from opengever.activity import notification_center
from opengever.activity.model.notification import Notification
from opengever.api.batch import SQLHypermediaBatch
from opengever.readonly import is_in_readonly_mode
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true
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

        if notification_id:
            return self.get_notification(userid, notification_id)
        return self.get_user_notifications()

    def get_notification(self, userid, notification_id):
        notification = self.center.get_notification(notification_id)
        if not notification:
            raise NotFound

        if not notification.userid == userid:
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")

        return self.serialize(notification)

    def get_user_notifications(self):
        notifications = self.center.get_current_users_notifications(badge_only=True)
        batch = SQLHypermediaBatch(self.request,
                                   notifications,
                                   unique_sort_key='id')

        result = {
            '@id': batch.canonical_url,
            'items_total': batch.items_total,
            'items': self.serialize(list(batch)),
        }

        if batch.links:
            result['batching'] = batch.links

        return result

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
        if mark_as_read and not is_in_readonly_mode():
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


class NotificationsPost(Service):
    """API endpoint to mark all notifications as read.

    POST /@notifications/peter.mueller HTTP/1.1

    Payload: {
        "mark_all_notifications_as_read": true,
        "latest_client_side_notification": <id>
    }
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(NotificationsPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@notifications as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, = self.read_params()
        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to access notifications of other users.")
        if not json_body(self.request).get('mark_all_notifications_as_read'):
            raise BadRequest(
                "Property 'mark_all_notifications_as_read' is required and must be true.")

        latest_notification_id = json_body(self.request).get('latest_client_side_notification')
        if not isinstance(latest_notification_id, int):
            raise BadRequest(
                "Property 'latest_client_side_notification' is required and must be an integer.")
        if Notification.query.by_user(userid).filter(
                Notification.notification_id == latest_notification_id).count() != 1:
            raise BadRequest(
                "User has no notification with notification_id {}.".format(latest_notification_id))

        notifications = (Notification.query.filter(
            Notification.userid == userid,
            Notification.is_badge == true(),
            Notification.is_read == false(),
            Notification.notification_id <= latest_notification_id).all())
        notification_ids = [n.notification_id for n in notifications]
        notification_center().mark_notifications_as_read(notification_ids)
        self.request.response.setStatus(204)
        return super(NotificationsPost, self).reply()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as path parameter.")

        return self.params
