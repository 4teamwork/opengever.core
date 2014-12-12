from opengever.activity.utils import notification_center
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NotificationViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('notification.pt')

    def __init__(self, context, request, view, manager=None):
        self.notifications = []

        super(NotificationViewlet, self).__init__(
            context, request, view, manager=manager)

    def num_unread(self):
        return len(self.fetch_notifications())

    def unread(self):
        return self.num_unread() > 0

    def fetch_notifications(self):
        if not self.notifications:
            center = notification_center()
            self.notifications = center.get_current_users_notifications()

        return self.notifications

    def get_notifications(self):
        notifications = []

        for notification in self.fetch_notifications():
            notifications.append({
                'activity': notification.activity,
                'link': '{}/resolve_oguid?oguid={}'.format(
                    self.context.absolute_url(),
                    notification.activity.resource.oguid),
                'read': notification.read})

        return notifications
