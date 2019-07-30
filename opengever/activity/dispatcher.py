from opengever.activity.model import NotificationDefault
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.model.settings import NotificationSetting
from opengever.base.model import create_session
from opengever.base.sentry import maybe_report_exception
from ZODB.POSException import ConflictError
import logging
import sys
import traceback


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

        dispatched_roles = self.get_dispatched_roles_for(notification.activity.kind, userid)
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

    def get_dispatched_roles_for(self, activity_kind, userid):
        """Returns a frozenset containing all activated notification-roles for
        the given activity_kind for the current dispatcher roles_key (digest,
        badge, mail).

        I.e. to get notified about added tasks through badge-notification if
        the user is marked as responsible, the user can select the specific setting
        within the notification-settings form.

        This function would return this selected role for the specific dispatcher.
        In our example, it would return:

        frozenset(['task_responsible'])

        for the badge-dispatcher
        """
        setting = self.get_setting(activity_kind, userid)
        fallback = frozenset([])
        return getattr(setting, self.roles_key, fallback) if setting else fallback

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
                maybe_report_exception(self.context, self.request, e_type, e_value, tb)
                not_dispatched.append(notifications)
                formatted_traceback = ''.join(traceback.format_exception(e_type, e_value, tb))
                logger.error('Exception while dispatch activity (MailDispatcher):\n%s', formatted_traceback)

        return not_dispatched

    def dispatch_notification(self, notification):
        raise NotImplementedError
