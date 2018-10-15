from opengever.activity.model import NotificationDefault
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.model.settings import NotificationSetting
from opengever.base.model import create_session
from ZODB.POSException import ConflictError
import logging
import pkg_resources
import sys
import traceback


try:
    pkg_resources.get_distribution('ftw.raven')
    from ftw.raven.reporter import maybe_report_exception
except pkg_resources.DistributionNotFound:
    HAS_RAVEN = False
else:
    HAS_RAVEN = True


logger = logging.getLogger('opengever.activity')


class NotificationDispatcher(object):
    """Dispatch notifications.

    Notifications are stored in SQL.
    """

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
        if not dispatched_roles:
            return False

        query = create_session().query(Watcher).join(Subscription)
        query = query.filter(
            Subscription.resource == notification.activity.resource)
        query = query.filter(Subscription.role.in_(dispatched_roles))

        for watcher in query:
            if userid in watcher.get_user_ids():
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

            except BaseException:
                e_type, e_value, tb = sys.exc_info()
                if HAS_RAVEN:
                    maybe_report_exception(self.context, self.request, e_type, e_value, tb)
                not_dispatched.append(notifications)
                formatted_traceback = ''.join(traceback.format_exception(e_type, e_value, tb))
                logger.error('Exception while dispatch activity (MailDispatcher):\n%s', formatted_traceback)

        return not_dispatched

    def dispatch_notification(self, notification):
        raise NotImplementedError
