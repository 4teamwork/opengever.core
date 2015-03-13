from ftw.builder import builder_registry
from opengever.activity.models import Activity
from opengever.activity.models import Notification
from opengever.activity.models import Resource
from opengever.activity.models import Watcher
from opengever.base.oguid import Oguid
from opengever.ogds.models.tests.builders import SqlObjectBuilder
from plone.app.testing import TEST_USER_ID


class ResourceBuilder(SqlObjectBuilder):

    mapped_class = Resource
    id_argument_name = 'resource_id'

    def oguid(self, oguid):
        self.arguments['oguid'] = Oguid.parse(oguid)
        return self

    def watchers(self, watchers):
        if isinstance(watchers, list):
            watchers = set(watchers)

        self.arguments['watchers'] = watchers
        return self

builder_registry.register('resource', ResourceBuilder)


class WatcherBuilder(SqlObjectBuilder):

    mapped_class = Watcher
    id_argument_name = 'watcher_id'

builder_registry.register('watcher', WatcherBuilder)


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

    def as_read(self):
        self.arguments['read'] = True
        return self

builder_registry.register('notification', NotificationBuilder)
