from opengever.activity import is_activity_feature_enabled
from opengever.activity import notification_center
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from time import time


class NotificationViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request, view, manager=None):
        self.notifications = []

        super(NotificationViewlet, self).__init__(
            context, request, view, manager=manager)

    def available(self):
        return is_activity_feature_enabled()

    def num_unread(self):
        center = notification_center()
        return center.count_current_users_unread_notifications(badge_only=True)

    @property
    def timestamp(self):
        return int(time())

    @property
    def read_url(self):
        return '{}/notifications/read'.format(self.context.absolute_url())

    @property
    def list_url(self):
        return '{}/notifications/list'.format(self.context.absolute_url())

    @property
    def overview_url(self):
        return '{}/personal_overview#mynotifications'.format(api.portal.get().absolute_url())
