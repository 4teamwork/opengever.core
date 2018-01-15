from opengever.activity.dispatcher import NotificationDispatcher


class DigestDispatcher(NotificationDispatcher):

    _id = 'digest'
    roles_key = 'digest_notification_roles'

    def dispatch_notification(self, notification):
        notification.digest = True
