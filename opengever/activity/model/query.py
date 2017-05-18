from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model import NotificationDefault
from opengever.activity.model import Resource
from opengever.activity.model.subscription import Subscription
from opengever.ogds.models.query import BaseQuery


class ActivityQuery(BaseQuery):
    pass

Activity.query_cls = ActivityQuery


class NotificationQuery(BaseQuery):

    def by_user(self, userid):
        return self.filter_by(userid=userid)

    def by_subscription_roles(self, roles, activity):
        subscriptions = Subscription.query.by_resource_and_role(
            activity.resource, roles)
        user_ids = []
        for subscription in subscriptions:
            user_ids += subscription.watcher.get_user_ids()

        return self.filter_by(activity_id=activity.id).filter(
            Notification.userid.in_(user_ids))

Notification.query_cls = NotificationQuery


class ResourceQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        return self.filter_by(oguid=oguid).first()

Resource.query_cls = ResourceQuery


class NotificationDefaultQuery(BaseQuery):

    def is_dispatch_needed(self, dispatch_setting, kind):
        setting = self.filter_by(kind=kind).first()
        if not setting:
            return False

        return getattr(setting, dispatch_setting, False)

    def by_kind(self, kind):
        return self.filter_by(kind=kind)

NotificationDefault.query_cls = NotificationDefaultQuery
