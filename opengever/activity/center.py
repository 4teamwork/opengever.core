from opengever.activity.error_handling import NotificationErrorHandler
from opengever.activity.events import WatcherAddedEvent
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from plone import api
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true
from zope.event import notify
from zope.globalrequest import getRequest


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

    def add_watcher(self, actorid):
        watcher = Watcher(actorid=actorid)
        self.session.add(watcher)
        return watcher

    def fetch_watcher(self, actorid):
        return Watcher.query.get_by_actorid(actorid)

    def add_watcher_to_resource(self, oguid, userid, role=WATCHER_ROLE,
                                omit_watcher_added_event=False):
        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        resource.add_watcher(userid, role)
        if role == WATCHER_ROLE and not omit_watcher_added_event:
            notify(WatcherAddedEvent(oguid, userid))

    def remove_watcher_from_resource(self, oguid, userid, role):
        watcher = self.fetch_watcher(userid)
        resource = self.fetch_resource(oguid)

        if watcher and resource and role:
            subscription = Subscription.query.fetch(resource, watcher, role)
            if subscription:
                self.session.delete(subscription)

    def remove_watchers_from_resource_by_role(self, oguid, role):
        resource = self.fetch_resource(oguid)
        subscriptions = Subscription.query.by_resource_and_role(
            resource, [role])

        if resource and subscriptions:
            map(self.session.delete, subscriptions.all())

            # The association-proxy objects "watchers" of the Resource object
            # are not update. We have to expire the slq-alchemy object to
            # let it refetch the relations.
            # See https://docs.sqlalchemy.org/en/latest/orm/session_state_management.html#refreshing-expiring
            # for more information about this issue.
            self.session.expire(resource)

    def get_watchers(self, oguid):
        """Returns a read-only tuple of watchers for a given oguid.
        """
        resource = Resource.query.get_by_oguid(oguid)
        if not resource:
            return ()

        # resources.watchers is an association_proxy. When not consumed properly
        # the GC will remove things, resulting in a "stale association proxy"
        # error. In order to avoid that we consume it by making a tuple.
        return tuple(resource.watchers)

    def get_subscriptions(self, oguid):
        resource = self.fetch_resource(oguid)
        if not resource:
            return ()

        # resources.subscriptions is an association_proxy. When not consumed properly
        # the GC will remove things, resulting in a "stale association proxy"
        # error. In order to avoid that we consume it by making a tuple.
        return tuple(resource.subscriptions)

    def add_activity(self, oguid, kind, title, label, summary, actor_id,
                     description, notification_recipients=None):
        """Creates an activity and the related notifications..
        """
        activity = self._add_activity(
            oguid, kind, title, label, summary, actor_id, description)

        errors = self.create_notifications(activity, notification_recipients)
        return {'activity': activity, 'errors': errors}

    def create_notifications(self, activity, notification_recipients=None):
        errors = []
        request = getRequest()
        if request:
            header = request.getHeader('X-GEVER-SuppressNotifications', default='')
            if header.lower() in ("yes", "y", "true", "t", "1"):
                return errors
        activity.create_notifications(notification_recipients)
        for dispatcher in self.dispatchers:
            result = dispatcher.dispatch_notifications(activity)
            errors += result

        return errors

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        query = Notification.query.by_user(userid)
        if only_unread:
            query = query.filter(Notification.is_read == false())

        query = query.join(
            Notification.activity).order_by(desc(Activity.created))
        return query.limit(limit).all()

    def count_users_unread_notifications(self, userid, badge_only=False):
        query = Notification.query.by_user(userid)
        if badge_only:
            query = query.filter(Notification.is_badge == true())
        return query.filter(Notification.is_read == false()).count()

    def mark_notification_as_read(self, notification_id):
        notification = self.get_notification(notification_id)
        notification.is_read = True

    def mark_notifications_as_read(self, ids):
        query = Notification.query.filter(
            Notification.notification_id.in_(ids))
        query.update(
            {Notification.is_read: True}, synchronize_session='fetch')

    def get_notification(self, notification_id):
        return Notification.get(notification_id)

    def list_notifications(self, userid=None, sort_on='created', filters=[],
                           sort_reverse=False, offset=0, limit=None,
                           badge_only=False):

        order = desc if sort_reverse else asc
        query = Notification.query
        if userid:
            query = query.by_user(userid)

        query = query.join(Notification.activity)
        if badge_only:
            query = query.filter(Notification.is_badge == true())
        query = query.order_by(order(sort_on))
        query = query.offset(offset).limit(limit)
        return query.options(contains_eager(Notification.activity)).all()

    def count_notifications(self, userid=None, filters=[]):
        query = Notification.query
        if userid:
            query = query.by_user(userid)

        query = query.join(Notification.activity)
        return query.count()

    def _add_activity(self, oguid, kind, title, label, summary, actor_id, description):
        """Creates an activity instance and add it to the database.
        """
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

        return activity


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

    def add_watcher_to_resource(self, obj, actorid, role=WATCHER_ROLE,
                                omit_watcher_added_event=False):
        """The WatcherAddedEvent is fired to prevent circular dependencies."""
        oguid = self._get_oguid_for(obj)
        super(PloneNotificationCenter, self).add_watcher_to_resource(
            oguid, actorid, role, omit_watcher_added_event)

    def remove_watcher_from_resource(self, obj, userid, role):
        oguid = self._get_oguid_for(obj)
        super(PloneNotificationCenter, self).remove_watcher_from_resource(
            oguid, userid, role)

    def remove_watchers_from_resource_by_role(self, obj, role):
        oguid = self._get_oguid_for(obj)
        super(PloneNotificationCenter, self).remove_watchers_from_resource_by_role(
            oguid, role)

    def add_task_responsible(self, obj, actorid):
        self.add_watcher_to_resource(obj, actorid, TASK_RESPONSIBLE_ROLE)

    def remove_task_responsible(self, obj, actorid):
        self.remove_watcher_from_resource(obj, actorid, TASK_RESPONSIBLE_ROLE)

    def add_task_issuer(self, obj, actorid):
        self.add_watcher_to_resource(obj, actorid, TASK_ISSUER_ROLE)

    def remove_task_issuer(self, obj, actorid):
        self.remove_watcher_from_resource(obj, actorid, TASK_ISSUER_ROLE)

    def add_activity(self, obj, kind, title, label, summary, actor_id, description,
                     notification_recipients=None):
        oguid = self._get_oguid_for(obj)
        with NotificationErrorHandler() as handler:
            result = super(PloneNotificationCenter, self).add_activity(
                oguid, kind, title, label, summary, actor_id, description, notification_recipients)
            if result.get('errors'):
                handler.show_not_notified_message()
            return result

    def get_watchers(self, obj):
        oguid = self._get_oguid_for(obj)
        return super(PloneNotificationCenter, self).get_watchers(oguid)

    def get_subscriptions(self, obj):
        oguid = self._get_oguid_for(obj)
        return super(PloneNotificationCenter, self).get_subscriptions(oguid)

    def fetch_resource(self, obj):
        oguid = self._get_oguid_for(obj)
        return super(PloneNotificationCenter, self).fetch_resource(oguid)

    def count_current_users_unread_notifications(self, badge_only=False):
        return super(PloneNotificationCenter, self).count_users_unread_notifications(
            api.user.get_current().getId(), badge_only)

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

    def add_watcher(self, actorid):
        pass

    def fetch_watcher(self, actorid):
        return None

    def add_watcher_to_resource(self, obj, userid, role=WATCHER_ROLE,
                                omit_watcher_added_event=False):
        pass

    def remove_watcher_from_resource(self, obj, userid, role):
        pass

    def remove_watchers_from_resource_by_role(self, obj, role):
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

    def get_subscriptions(self, oguid):
        return []

    def add_activity(self, obj, kind, title, label, summary, actor_id, description,
                     notification_recipients=None):
        pass

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        return []

    def mark_notification_as_read(self, notification_id):
        pass

    def get_current_users_notifications(self, only_unread=False, limit=None):
        return []
