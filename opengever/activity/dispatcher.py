import logging
import sys
import traceback
from opengever.activity.model import NotificationDefault
from ZODB.POSException import ConflictError


logger = logging.getLogger('opengever.activity')


class NotificationDispatcher(object):

    enabled_key = None
    roles_key = None

    def get_setting(self, kind):
        return NotificationDefault.query.by_kind(kind=kind).first()

    def get_roles_to_dispatch(self, kind):
        setting = self.get_setting(kind)
        if not setting:
            return []

        return getattr(setting, self.roles_key)

    def dispatch_notifications(self, activity):
        not_dispatched = []
        roles = self.get_roles_to_dispatch(activity.kind)
        notifications = activity.get_notifications_for_watcher_roles(roles)

        for notification in notifications:
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
