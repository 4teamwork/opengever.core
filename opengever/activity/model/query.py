from opengever.activity.model import Activity
from opengever.activity.model import Digest
from opengever.activity.model import Notification
from opengever.activity.model import NotificationDefault
from opengever.activity.model import Resource
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.base.query import BaseQuery
from sqlalchemy import and_
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true


class ActivityQuery(BaseQuery):
    """Provide accessors to activity."""


Activity.query_cls = ActivityQuery


class NotificationQuery(BaseQuery):
    """Provide accessors to notifications."""

    def by_user(self, userid):
        return self.filter_by(userid=userid)

    def by_subscription_roles(self, roles, activity):
        subscriptions = Subscription.query.by_resource_and_role(activity.resource, roles)
        user_ids = [user_id for subscription in subscriptions for user_id in subscription.watcher.get_user_ids()]

        if user_ids:
            return self.filter_by(activity_id=activity.id).filter(Notification.userid.in_(user_ids))

        return self.filter_by(activity_id=activity.id).filter(Notification.userid.is_(None))

    def unsent_digest_notifications(self):
        return self.filter(and_(Notification.is_digest == true(),
                                Notification.sent_in_digest == false()))


Notification.query_cls = NotificationQuery


class ResourceQuery(BaseQuery):
    """Provide accessors to resources."""

    def get_by_oguid(self, oguid):
        return self.filter_by(oguid=oguid).first()


Resource.query_cls = ResourceQuery


class NotificationDefaultQuery(BaseQuery):
    """Provide a default accessors to activities."""

    def is_dispatch_needed(self, dispatch_setting, kind):
        setting = self.filter_by(kind=kind).first()
        if not setting:
            return False

        return getattr(setting, dispatch_setting, False)

    def by_kind(self, kind):
        return self.filter_by(kind=kind)


NotificationDefault.query_cls = NotificationDefaultQuery


class SubscriptionQuery(BaseQuery):
    """Provide accessors to subscriptions."""

    def fetch(self, resource, watcher, role):
        return self.filter_by(
            resource=resource, watcher=watcher, role=role).first()

    def get_by_watcher_resource(self, resource, watcher):
        return self.filter_by(resource=resource, watcher=watcher).first()

    def by_resource_and_role(self, resource, roles):
        if roles:
            return self.filter_by(resource=resource).filter(Subscription.role.in_(roles))

        return self.filter_by(resource=resource).filter(Subscription.role.is_(None))


Subscription.query_cls = SubscriptionQuery


class WatcherQuery(BaseQuery):
    """Provide accessors to watchers."""

    def get_by_actorid(self, actorid):
        return self.filter_by(actorid=actorid).first()


Watcher.query_cls = WatcherQuery


class DigestQuery(BaseQuery):
    """Provide accessors to digests."""

    def get_by_userid(self, userid):
        return self.filter_by(userid=userid).first()


Digest.query_cls = DigestQuery
