from ftw.builder import builder_registry
from opengever.activity.model import Activity
from opengever.activity.model import Digest
from opengever.activity.model import Notification
from opengever.activity.model import NotificationDefault
from opengever.activity.model import NotificationSetting
from opengever.activity.model import Resource
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.oguid import Oguid
from opengever.testing.builders.base import TEST_USER_ID
from opengever.testing.builders.sql import SqlObjectBuilder


class ResourceBuilder(SqlObjectBuilder):

    mapped_class = Resource
    id_argument_name = 'resource_id'

    def __init__(self, session):
        super(ResourceBuilder, self).__init__(session)
        self._watchers = []

    def oguid(self, oguid):
        self.arguments['oguid'] = Oguid.parse(oguid)
        return self

    def watchers(self, watchers):
        if isinstance(watchers, list):
            watchers = set(watchers)

        self._watchers = watchers
        return self

    def after_create(self, obj):
        for watcher in self._watchers:
            obj.add_watcher(watcher.actorid, WATCHER_ROLE)
        return obj


builder_registry.register('resource', ResourceBuilder)


class WatcherBuilder(SqlObjectBuilder):

    mapped_class = Watcher
    id_argument_name = 'watcher_id'


builder_registry.register('watcher', WatcherBuilder)


class SubscriptionBuilder(SqlObjectBuilder):

    mapped_class = Subscription


builder_registry.register('subscription', SubscriptionBuilder)


class ActivityBuilder(SqlObjectBuilder):

    mapped_class = Activity
    id_argument_name = 'activity_id'

    def __init__(self, session):
        super(ActivityBuilder, self).__init__(session)
        self.arguments['kind'] = 'task-added'
        self.arguments['title'] = 'Kennzahlen 2014 erfassen'
        self.arguments['summary'] = 'Task created by Test User'
        self.arguments['actor_id'] = TEST_USER_ID


builder_registry.register('activity', ActivityBuilder)


class NotificationBuilder(SqlObjectBuilder):

    mapped_class = Notification
    id_argument_name = 'notification_id'

    def __init__(self, session):
        super(NotificationBuilder, self).__init__(session)
        self.arguments['is_badge'] = True

    def watcher(self, watcher):
        self.arguments['userid'] = watcher.actorid
        return self

    def as_read(self):
        self.arguments['is_read'] = True
        return self


builder_registry.register('notification', NotificationBuilder)


class NotificationDefaultBuilder(SqlObjectBuilder):

    mapped_class = NotificationDefault


builder_registry.register('notification_default_setting',
                          NotificationDefaultBuilder)


class NotificationSettingBuilder(SqlObjectBuilder):

    mapped_class = NotificationSetting


builder_registry.register('notification_setting', NotificationSettingBuilder)


class DigestBuilder(SqlObjectBuilder):

    mapped_class = Digest


builder_registry.register('digest', DigestBuilder)
