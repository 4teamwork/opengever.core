from opengever.activity.utils import notification_center
from Products.Five import BrowserView


class NotificationView(BrowserView):
    """Notfication JSON API used for the viewlet."""

    def read(self):
        """Mark the notification given as request parameter `notification_id`
        as read.
        """
        notification_id = self.request.get('notification_id')
        notification_center().mark_notification_as_read(notification_id)
        return True
