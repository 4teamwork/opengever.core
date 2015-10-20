from five import grok
from opengever.activity import notification_center
from opengever.activity.browser import resolve_notification_url
from opengever.activity.browser.listing import NotificationListingTab
from plone import api
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
import json
import pytz


class NotificationView(BrowserView):

    def read(self):
        """Mark the notification passed as request parameter `notification_id`
        or multiple notification ids as json list via the `notification_ids`
        parameter as read.
        """
        notification_id = self.request.get('notification_id')
        notification_ids = self.request.get('notification_ids')

        if notification_id:
            return notification_center().mark_notification_as_read(
                int(notification_id))

        elif notification_ids:
            return notification_center().mark_notifications_as_read(
                json.loads(notification_ids))

        else:
            raise AttributeError

    def list(self):
        """Returns a json representation of the current users notifications.
        """
        center = notification_center()

        # batching
        batch_size = int(self.request.get('batch_size', 10))
        page = int(self.request.get('page', 0))
        offset = page * batch_size

        notifications = center.list_notifications(
            api.user.get_current().getId(),
            limit=batch_size,
            offset=offset)

        data = {
            'next_page': self.get_next_batch_url(page, batch_size),
            'notifications': self.dump_notifications(notifications)}
        return self.json_respone(data)

    def get_next_batch_url(self, current_page, batch_size):
        return '{}/notifications/list?page={}&batch_size={}'.format(
            self.context.absolute_url(), current_page + 1, batch_size)

    def json_respone(self, data):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        return json.dumps(data)

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
                'read': notification.is_read,
                'id': notification.notification_id})

        return data


class MyNotifications(NotificationListingTab):
    grok.name('tabbedview_view-mynotifications')
    grok.context(Interface)

    enabled_actions = []
    major_actions = []

    selection = ViewPageTemplateFile("no_selection.pt")

    def get_base_query(self):
        return {'userid': api.user.get_current().getId()}
