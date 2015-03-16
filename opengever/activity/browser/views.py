from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.activity import _
from opengever.activity import notification_center
from opengever.activity.browser.listing import NotificationListingTab
from opengever.activity.models.notification import Notification
from plone import api
from Products.Five import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import Interface


class NotificationView(BrowserView):

    def read(self):
        """Mark the notification passed as request parameter `notification_id`
        as read.
        """
        notification_id = self.request.get('notification_id')
        notification_center().mark_notification_as_read(notification_id)
        return True


class NotificationOverview(TabbedView):

    def get_tabs(self):
        tabs = [
            {'id': 'mynotifications',
             'icon': None,
             'url': '#',
             'class': None,
             'title':_('label_my_notifications', default=u'My notifications')},
        ]

        return tabs


class MyNotifications(NotificationListingTab):
    grok.name('tabbedview_view-mynotifications')
    grok.context(Interface)

    enabled_actions = []
    major_actions = []

    selection = ViewPageTemplateFile("no_selection.pt")

    def get_base_query(self):
        userid = api.user.get_current().getId()
        return Notification.query.by_user(userid)
