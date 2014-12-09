from ftw.builder import Builder
from ftw.builder import create
from opengever.activity import Resource
from opengever.activity import Watcher
from opengever.activity.notification_center import NotificationCenter
from opengever.activity.tests.base import ActivityTestCase
from opengever.globalindex.oguid import Oguid
from sqlalchemy.exc import IntegrityError


class TestResourceHandling(ActivityTestCase):

    def setUp(self):
        super(TestResourceHandling, self).setUp()
        self.center = NotificationCenter()

    def test_fetch_return_resource_by_means_of_oguid(self):
        resource_a = create(Builder('resource').oguid('fd:123'))
        resource_b = create(Builder('resource').oguid('fd:456'))

        self.assertEquals(resource_a, self.center.fetch_resource('fd:123'))
        self.assertEquals(resource_b, self.center.fetch_resource('fd:456'))

    def test_fetch_return_none_when_resource_not_exists(self):
        self.assertEquals(None, self.center.fetch_resource('fd:123'))

    # def test_reaadd_existing_resource_raises_integrity_error(self):
    #     self.center.add_resource('fd:123')

    #     with self.assertRaises(IntegrityError):
    #         self.center.add_resource('fd:123')
    #         self.session.flush()

    def test_adding(self):
        resource = self.center.add_resource(Oguid(id='fd:123'))

        self.assertEquals(1, len(Resource.query.all()))
        resource = Resource.query.first()
        self.assertEquals(Oguid(id='fd:123'), resource.oguid)
        self.assertEquals('fd', resource.admin_unit_id)
        self.assertEquals(123, resource.int_id)


class TestWatcherHandling(ActivityTestCase):

    def setUp(self):
        super(TestWatcherHandling, self).setUp()
        self.center = NotificationCenter()

    def test_fetch_returns_watcher_by_means_of_user_id(self):
        hugo = create(Builder('watcher').having(user_id='hugo'))
        peter = create(Builder('watcher').having(user_id='peter'))

        self.assertEquals(hugo, self.center.fetch_watcher('hugo'))
        self.assertEquals(peter, self.center.fetch_watcher('peter'))

    def test_return_none_when_watcher_not_exists(self):
        self.assertEquals(None, self.center.fetch_watcher('peter'))

    def test_adding(self):
        peter = self.center.add_watcher('peter')

        self.assertEquals(1, len(Watcher.query.all()))
        self.assertEquals('peter', Watcher.query.first().user_id)

    def test_add_watcher_to_resource_creates_resource_when_not_exitst(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource('fd:123', 'peter')

        self.assertEquals([peter], resource.watchers)

    def test_add_watcher_to_resource_creates_resource_when_not_exitst(self):
        peter = create(Builder('watcher').having(user_id='peter'))

        self.center.add_watcher_to_resource(Oguid(id='fd:123'), 'peter')

        resource = peter.resources[0]
        self.assertEquals('fd:123', resource.oguid)

    def test_add_watcher_to_resource_creates_watcher_when_not_exitst(self):
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource('fd:123', 'peter')

        watcher = resource.watchers[0]
        self.assertEquals('peter', watcher.user_id)

    def test_get_watchers_returns_a_list_of_resource_watchers(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))
        fritz = create(Builder('watcher').having(user_id='fritz'))

        resource_a = create(Builder('resource')
                            .oguid('fd:123')
                            .having(watchers=[hugo, fritz]))
        resource_b = create(Builder('resource')
                            .oguid('fd:456')
                            .having(watchers=[peter]))

        self.assertEquals([hugo, fritz],
                          self.center.get_watchers('fd:123'))
        self.assertEquals([peter],
                          self.center.get_watchers('fd:456'))

    def test_get_watchers_returns_empty_list_when_resource_not_exists(self):
        self.assertEquals([], self.center.get_watchers('fd:123'))

    def test_remove_watcher_from_resource_raise_exception_when_watcher_not_exists(self):
        resource = create(Builder('resource').oguid('fd:123'))

        with self.assertRaises(Exception) as cm:
            self.center.remove_watcher_from_resource('fd:123', 'peter')

        self.assertEquals('Watcher with userid peter not found.',
                          str(cm.exception))

    def test_remove_watcher_from_resource_raise_exception_when_resource_not_exists(self):
        peter = create(Builder('watcher').having(user_id='peter'))

        with self.assertRaises(Exception) as cm:
            self.center.remove_watcher_from_resource('fd:123', 'peter')

        self.assertEquals('Resource with oguid fd:123 not found.',
                          str(cm.exception))

    def test_remove_watcher_from_resource(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))
        resource = create(Builder('resource')
                          .oguid('fd:123')
                          .having(watchers=[hugo, peter]))

        self.center.remove_watcher_from_resource('fd:123', 'peter')

        self.assertEquals([hugo], resource.watchers)


class TestAddActivity(ActivityTestCase):

    def setUp(self):
        super(TestAddActivity, self).setUp()
        self.center = NotificationCenter()

    def test_add_resource_if_not_exists(self):
        self.center.add_acitivity(Oguid(id='fd:123'),
                                  'TASK_ADDED',
                                  'Task bla added',
                                  'hugo.boss')

        resource = self.center.fetch_resource('fd:123')
        self.assertEquals('fd', resource.admin_unit_id)
        self.assertEquals(123, resource.int_id)

    def test_creates_notifications_for_each_resource_watcher(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))

        resource_a = create(Builder('resource').oguid('fd:123')
                            .having(watchers=[hugo, peter]))

        activity = self.center.add_acitivity('fd:123',
                                             'TASK_ADDED',
                                             'Task bla added',
                                             'hugo.boss')

        notification = peter.notifications[0]
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.read)

        notification = hugo.notifications[0]
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.read)
