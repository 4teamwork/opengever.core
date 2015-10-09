from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.model.subscription import TASK_ISSUER_ROLE
from opengever.activity.model.subscription import TASK_RESPONSIBLE_ROLE
from opengever.activity.model.subscription import WATCHER_ROLE
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.base.actor import Actor
from plone import api
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import desc
from ZODB.POSException import ConflictError
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory
import logging
import sys
import traceback


_ = MessageFactory("opengever.activity")
logger = logging.getLogger('opengever.activity')


class NotificationCenter(object):
    """
    The NotificationCenter is the key element of the complete activity and
    notification functionality. All queries and inputs from the plone site
    of opengever, should be done with the Notification Center.

    So we make sure that the NotificationCenter is completly separated from
    plone. This rise the testability and at a later date the NotificationCenter
    could be run as an external service.

    Keyword arguments:
    dispatchers -- a list of notification dispatchers (see
    PloneNotificationMailer as example)
    """

    def __init__(self, dispatchers=None):
        self.dispatchers = dispatchers or []
        self.session = create_session()

    def add_resource(self, oguid):
        resource = Resource(oguid=oguid)
        self.session.add(resource)
        return resource

    def fetch_resource(self, oguid):
        """Returns a resource by it's Oguid object or None when it does
        not exist.
        """
        resource = Resource.query.get_by_oguid(oguid)
        return resource

    def add_watcher(self, user_id):
        watcher = Watcher(user_id=user_id)
        self.session.add(watcher)
        return watcher

    def fetch_watcher(self, user_id):
        return Watcher.query.get_by_userid(user_id)

    def add_watcher_to_resource(self, oguid, userid, role=WATCHER_ROLE):
        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        resource.add_watcher(userid, role)

    def remove_watcher_from_resource(self, oguid, userid, role):
        watcher = self.fetch_watcher(userid)
        resource = self.fetch_resource(oguid)

        if watcher and resource and role:
            subscription = Subscription.query.fetch(resource, watcher, role)
            if subscription:
                self.session.delete(subscription)

    def get_watchers(self, oguid):
        resource = Resource.query.get_by_oguid(oguid)
        if not resource:
            return []

        return resource.watchers

    def add_activity(self, oguid, kind, title, label, summary, actor_id, description):
        if description is None:
            description = {}

        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        activity = Activity(resource=resource, kind=kind, actor_id=actor_id)

        # language dependent attributes
        for language, value in label.items():
            activity.translations[language].label = value

        for language, value in summary.items():
            activity.translations[language].summary = value

        for language, value in description.items():
            activity.translations[language].description = value

        for language, value in title.items():
            activity.translations[language].title = value

        self.session.add(activity)

        errors = self.create_notifications(activity)
        return {'activity': activity, 'errors': errors}

    def create_notifications(self, activity):
        activity.create_notifications()
        errors = []
        for dispatcher in self.dispatchers:
            result = dispatcher.dispatch_notifications(activity)
            errors += result

        return errors

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        query = Notification.query.by_user(userid)
        if only_unread:
            query = query.filter(Notification.is_read == False)

        query = query.join(
            Notification.activity).order_by(desc(Activity.created))
        return query.limit(limit).all()

    def mark_notification_as_read(self, notification_id):
        notification = self.get_notification(notification_id)
        notification.is_read = True

    def get_notification(self, notification_id):
        return Notification.get(notification_id)

    def list_notifications(self, userid=None, sort_on='created', filters=[],
                                     sort_reverse=False, offset=0, limit=None):

        order = desc if sort_reverse else asc
        query = Notification.query.join(Notification.activity)
        if userid:
            query = query.by_user(userid)

        query = query.order_by(order(sort_on))
        query = query.offset(offset).limit(limit)
        return query.options(contains_eager(Notification.activity)).all()


class PloneNotificationCenter(NotificationCenter):
    """The PloneNotificationCenter is a wrapper of the NotificationCenter,
    which provides some helper methods for easier access directly from plone.
    """

    def _get_oguid_for(self, item):
        """Helper which returns a oguid for a given item. If the item is
        already an oguid, this oguid is returned."""

        if not isinstance(item, Oguid):
            return Oguid.for_object(item)
        return item

    def add_watcher_to_resource(self, obj, actorid, role):
        actor = Actor.lookup(actorid)
        oguid = self._get_oguid_for(obj)
        for representative in actor.representatives():
            super(PloneNotificationCenter, self).add_watcher_to_resource(
                oguid, representative.userid, role)

    def remove_watcher_from_resource(self, obj, userid, role):
        oguid = self._get_oguid_for(obj)
        super(PloneNotificationCenter, self).remove_watcher_from_resource(
            oguid, userid, role)

    def add_task_responsible(self, obj, actorid):
        self.add_watcher_to_resource(obj, actorid, TASK_RESPONSIBLE_ROLE)

    def remove_task_responsible(self, obj, actorid):
        self.remove_watcher_from_resource(obj, actorid, TASK_RESPONSIBLE_ROLE)

    def add_task_issuer(self, obj, actorid):
        self.add_watcher_to_resource(obj, actorid, TASK_ISSUER_ROLE)

    def remove_task_issuer(self, obj, actorid):
        self.remove_watcher_from_resource(obj, actorid, TASK_ISSUER_ROLE)

    def add_activity(self, obj, kind, title, label, summary, actor_id, description):
        oguid = self._get_oguid_for(obj)
        try:
            result = super(PloneNotificationCenter, self).add_activity(
                oguid, kind, title, label, summary, actor_id, description)
            if result.get('errors'):
                self.show_not_notified_message()

        except ConflictError:
            raise

        except Exception:
            self.show_not_notified_message()
            tcb = ''.join(traceback.format_exception(*sys.exc_info()))
            logger.error('Exception while adding an activity:\n{}'.format(tcb))

        return

    def show_not_notified_message(self):
        msg = _(u'msg_error_not_notified',
                default=u'A problem has occurred during the notification '
                'creation. Notification could not or only partially '
                'produced.')
        api.portal.show_message(msg, getRequest(), type='warning')

    def get_watchers(self, obj):
        oguid = self._get_oguid_for(obj)
        return super(PloneNotificationCenter, self).get_watchers(oguid)

    def fetch_resource(self, obj):
        oguid = self._get_oguid_for(obj)
        return super(PloneNotificationCenter, self).fetch_resource(oguid)

    def get_current_users_notifications(self, only_unread=False, limit=None):
        return super(PloneNotificationCenter, self).get_users_notifications(
            api.user.get_current().getId(),
            only_unread=only_unread,
            limit=limit)


class DisabledNotificationCenter(NotificationCenter):
    """The DisabledNotificationCenter is returned from the
    `notification_center` helper, when the activity feature is disabled.
    """

    def add_resource(self, oguid):
        pass

    def fetch_resource(self, oguid):
        return None

    def add_watcher(self, user_id):
        pass

    def fetch_watcher(self, user_id):
        return None

    def add_watcher_to_resource(self, obj, userid, role):
        pass

    def remove_watcher_from_resource(self, obj, userid, role):
        pass

    def add_task_responsible(self, obj, actorid):
        pass

    def remove_task_responsible(self, obj, actorid):
        pass

    def add_task_issuer(self, obj, actorid):
        pass

    def remove_task_issuer(self, obj, actorid):
        pass

    def get_watchers(self, obj):
        return []

    def add_activity(self, obj, kind, title, label, summary, actor_id, description):
        pass

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        return []

    def mark_notification_as_read(self, notification_id):
        pass

    def get_current_users_notifications(self, only_unread=False, limit=None):
        return []
