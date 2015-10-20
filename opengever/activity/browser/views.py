from five import grok
from opengever.activity import notification_center
from opengever.activity.browser.listing import NotificationListingTab
from plone import api
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface
import json


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


class MyNotifications(NotificationListingTab):
    grok.name('tabbedview_view-mynotifications')
    grok.context(Interface)

    enabled_actions = []
    major_actions = []

    selection = ViewPageTemplateFile("no_selection.pt")

    def get_base_query(self):
        return {'userid': api.user.get_current().getId()}
