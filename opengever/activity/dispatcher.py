from opengever.activity.model import NotificationDefault
from opengever.activity.model import Subscription
from opengever.activity.model.settings import NotificationSetting
from ZODB.POSException import ConflictError
import logging
import sys
import traceback


logger = logging.getLogger('opengever.activity')


class NotificationDispatcher(object):

    enabled_key = None
    roles_key = None

    def get_setting(self, kind, userid):
        setting = NotificationSetting.query.filter_by(
            kind=kind, userid=userid).first()
        if setting:
            return setting

        return NotificationDefault.query.by_kind(kind=kind).first()

    def dispatch_needed(self, notification):
        userid = notification.userid
        setting = self.get_setting(notification.activity.kind, userid)
        if not setting:
            return False

        dispatched_roles = getattr(setting, self.roles_key)
        subscriptions = Subscription.query.filter_by(
            resource=notification.activity.resource)

        for subscription in subscriptions:
            if subscription.role in dispatched_roles:
                if userid in subscription.watcher.get_user_ids():
                    return True

        return False

    def dispatch_notifications(self, activity):
        not_dispatched = []
        notifications = activity.notifications

        for notification in notifications:
            if not self.dispatch_needed(notification):
                continue

            try:
                self.dispatch_notification(notification)
            except ConflictError:
                raise

            except Exception:
                not_dispatched.append(notifications)
                tcb = ''.join(traceback.format_exception(*sys.exc_info()))
                logger.error('Exception while dispatch activity '
                             '(MailDispatcher):\n{}'.format(tcb))

        return not_dispatched

    def dispatch_notification(self, notification):
        raise NotImplementedError
