from opengever.activity.mail import PloneNotificationMailer
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.activity.model import Watcher
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.base.actor import Actor
from opengever.ogds.models.query import extend_query_with_textfilter
from plone import api
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import desc


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
        return Resource.query.get_by_oguid(oguid)

    def add_watcher(self, user_id):
        watcher = Watcher(user_id=user_id)
        self.session.add(watcher)
        return watcher

    def fetch_watcher(self, user_id):
        return Watcher.query.get_by_userid(user_id)

    def add_watcher_to_resource(self, oguid, userid):
        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        resource.add_watcher(userid)

    def remove_watcher_from_resource(self, oguid, userid):
        watcher = self.fetch_watcher(userid)
        resource = self.fetch_resource(oguid)

        if watcher and resource:
            resource.remove_watcher(watcher)

    def get_watchers(self, oguid):
        resource = Resource.query.get_by_oguid(oguid)
        if not resource:
            return []

        return resource.watchers

    def add_activity(self, oguid, kind, title, summary, actor_id, description=u''):
        resource = self.fetch_resource(oguid)
        if not resource:
            resource = self.add_resource(oguid)

        activity = Activity(resource=resource, kind=kind, title=title,
                            summary=summary, actor_id=actor_id,
                            description=description)
        self.session.add(activity)

        self.create_notifications(activity)

        return activity

    def create_notifications(self, activity):
        notifications = activity.create_notifications()
        for dispatcher in self.dispatchers:
            dispatcher.dispatch_notifications(notifications)

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        query = Notification.query.by_user(userid)
        if only_unread:
            query = query.filter(Notification.read == False)

        return query.limit(limit).all()

    def mark_notification_as_read(self, notification_id):
        notification = self.get_notification(notification_id)
        notification.read = True

    def get_notification(self, notification_id):
        return Notification.get(notification_id)

    def list_notifications(self, userid=None, sort_on='title', filters=[],
                                     sort_reverse=False, offset=0, limit=None):

        order = desc if sort_reverse else asc
        fields = [Activity.kind, Activity.title, Activity.actor_id]

        query = Notification.query.join(Notification.activity)
        if userid:
            query = query.by_user(userid)

        query = extend_query_with_textfilter(query, fields, filters)
        query = query.order_by(order(sort_on))
        query = query.offset(offset).limit(limit)
        return query.options(contains_eager(Notification.activity)).all()


class PloneNotificationCenter(NotificationCenter):
    """The PloneNotificationCenter is a wrapper of the NotificationCenter,
    which provides some helper methods for easier access directly from plone.
    """

    def __init__(self):
        dispatchers = [PloneNotificationMailer()]
        super(PloneNotificationCenter, self).__init__(dispatchers)

    def add_watcher_to_resource(self, obj, actorid):
        actor = Actor.lookup(actorid)
        oguid = Oguid.for_object(obj)
        for representative in actor.representatives():
            super(PloneNotificationCenter, self).add_watcher_to_resource(
                oguid, representative.userid)

    def remove_watcher_from_resource(self, obj, userid):
        oguid = Oguid.for_object(obj)
        super(PloneNotificationCenter, self).remove_watcher_from_resource(
            oguid, userid)

    def add_activity(self, obj, kind, title, summary, actor_id, description=u''):
        oguid = Oguid.for_object(obj)

        return super(PloneNotificationCenter, self).add_activity(
            oguid, kind, title, summary, actor_id, description=description)

    def get_watchers(self, obj):
        oguid = Oguid.for_object(obj)
        return super(PloneNotificationCenter, self).get_watchers(oguid)

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

    def add_watcher_to_resource(self, obj, userid):
        pass

    def remove_watcher_from_resource(self, obj, userid):
        pass

    def get_watchers(self, obj):
        return []

    def add_activity(self, obj, kind, title, summary, actor_id, description=u''):
        pass

    def get_users_notifications(self, userid, only_unread=False, limit=None):
        return []

    def mark_notification_as_read(self, notification_id):
        pass

    def get_current_users_notifications(self, only_unread=False, limit=None):
        return []
