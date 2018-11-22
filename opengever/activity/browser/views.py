from opengever.activity import notification_center
from opengever.activity.browser import resolve_notification_url
from opengever.activity.browser.listing import NotificationListingTab
from plone import api
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
import json
import pytz


class NotificationView(BrowserView):

    def read(self):
        """Mark the notification passed as request parameter `notification_id`
        or multiple notification ids as json list via the `notification_ids`
        parameter as read.
        """

        notification_ids = self.request.get('notification_ids')
        if not notification_ids:
            raise Exception('Missing parameter `notification_ids`')

        return notification_center().mark_notifications_as_read(
            json.loads(notification_ids))

    def list(self):
        """Returns a json representation of the current users notifications.
        """
        center = notification_center()
        current_user_id = api.user.get_current().getId()

        # batching
        batch_size = int(self.request.get('batch_size', 10))
        page = int(self.request.get('page', 1))
        offset = (page - 1) * batch_size

        total = center.count_notifications(current_user_id)
        notifications = center.list_notifications(
            current_user_id,
            limit=batch_size,
            sort_reverse=True,
            offset=offset,
            badge_only=True)

        next_url = self.get_next_batch_url(page, batch_size, total, offset)
        return self.json_response({
            'next_page': next_url,
            'notifications': self.dump_notifications(notifications)})

    def get_next_batch_url(self, current_page, batch_size, total, offset):
        """Checks if there is a next page, thus it returns the prepared url
        otherwise it returns None
        """
        if total > offset + batch_size:
            return '{}/notifications/list?page={}&batch_size={}'.format(
                self.context.absolute_url(), current_page + 1, batch_size)
        return None

    def json_response(self, data):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        return json.dumps(data)

    def get_link_target(self, notification):
        oguid =  notification.activity.resource.oguid
        if oguid.is_on_current_admin_unit:
            return '_self'

        return '_blank'

    def dump_notifications(self, notifications):
        data = []
        for notification in notifications:
            data.append({
                'title': notification.activity.title,
                'label': notification.activity.label,
                'summary': notification.activity.summary,
                'created': notification.activity.created.astimezone(
                    pytz.UTC).isoformat(),
                'link': resolve_notification_url(notification),
                'target': self.get_link_target(notification),
                'read': notification.is_read,
                'id': notification.notification_id})

        return data


class MyNotifications(NotificationListingTab):

    enabled_actions = []
    major_actions = []

    selection = ViewPageTemplateFile("no_selection.pt")

    def get_base_query(self):
        return {'userid': api.user.get_current().getId()}
