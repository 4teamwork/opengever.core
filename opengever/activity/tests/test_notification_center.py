from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.center import NotificationCenter
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.activity.model import Watcher
from opengever.activity.tests.base import ActivityTestCase
from opengever.base.oguid import Oguid
from sqlalchemy.exc import IntegrityError
import transaction
import unittest


class TestResourceHandling(ActivityTestCase):

    def setUp(self):
        super(TestResourceHandling, self).setUp()
        self.center = NotificationCenter()

    def test_fetch_return_resource_by_means_of_oguid(self):
        resource_a = create(Builder('resource').oguid('fd:123'))
        resource_b = create(Builder('resource').oguid('fd:456'))

        self.assertEquals(resource_a,
                          self.center.fetch_resource(Oguid('fd', '123')))
        self.assertEquals(resource_b,
                          self.center.fetch_resource(Oguid('fd', '456')))

    def test_fetch_return_none_when_resource_not_exists(self):
        self.assertEquals(None,
                          self.center.fetch_resource(Oguid('fd', '123')))

    def test_adding(self):
        resource = self.center.add_resource(Oguid('fd', '123'))

        self.assertEquals(1, len(Resource.query.all()))
        resource = Resource.query.first()
        self.assertEquals(Oguid('fd', '123'), resource.oguid)
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
        self.center.add_watcher('peter')

        self.assertEquals(1, len(Watcher.query.all()))
        self.assertEquals('peter', Watcher.query.first().user_id)

    def test_add_watcher_twice_raise_integrity_error(self):
        self.center.add_watcher('peter')
        with self.assertRaises(IntegrityError):
            self.center.add_watcher('peter')
            transaction.commit()

        transaction.abort()

    def test_add_watcher_to_resource(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(Oguid('fd', '123'), 'peter')

        self.assertEquals([peter], list(resource.watchers))

    def test_adding_watcher_twice_to_resource_is_ignored(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(Oguid('fd', '123'), 'peter')
        self.center.add_watcher_to_resource(Oguid('fd', '123'), 'peter')

        self.assertEquals([peter], list(resource.watchers))

    def test_add_watcher_to_resource_creates_resource_when_not_exitst(self):
        peter = create(Builder('watcher').having(user_id='peter'))

        self.center.add_watcher_to_resource(Oguid('fd', '123'), 'peter')

        resource = peter.resources[0]
        self.assertEquals('fd:123', resource.oguid)

    def test_add_watcher_to_resource_creates_watcher_when_not_exitst(self):
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(Oguid('fd', '123'), 'peter')

        watcher = list(resource.watchers)[0]
        self.assertEquals('peter', watcher.user_id)

    def test_get_watchers_returns_a_list_of_resource_watchers(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))
        fritz = create(Builder('watcher').having(user_id='fritz'))

        create(Builder('resource').oguid('fd:123').watchers([hugo, fritz]))
        create(Builder('resource').oguid('fd:456').watchers([peter]))

        self.assertEquals(set([hugo, fritz]),
                          self.center.get_watchers(Oguid('fd', '123')))
        self.assertEquals(set([peter]),
                          self.center.get_watchers(Oguid('fd', '456')))

    def test_get_watchers_returns_empty_list_when_resource_not_exists(self):
        self.assertEquals([], self.center.get_watchers(Oguid('fd', '123')))

    def test_remove_watcher_from_resource_will_be_ignored_when_watcher_not_exists(self):
        create(Builder('resource').oguid('fd:123'))

        self.center.remove_watcher_from_resource(Oguid('fd', '123'), 'peter')

    def test_remove_watcher_from_resource_will_be_ignored_when_resource_not_exists(self):
        create(Builder('watcher').having(user_id='peter'))

        self.center.remove_watcher_from_resource(Oguid('fd', '123'), 'peter')

    def test_remove_watcher_from_resource(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))
        resource = create(Builder('resource')
                          .oguid('fd:123')
                          .watchers([hugo, peter]))

        self.center.remove_watcher_from_resource(Oguid('fd', '123'), 'peter')

        self.assertEquals(set([hugo]), resource.watchers)


class TestAddActivity(ActivityTestCase):

    def setUp(self):
        super(TestAddActivity, self).setUp()
        self.center = NotificationCenter()

    def test_add_resource_if_not_exists(self):
        self.center.add_activity(
            Oguid('fd', '123'),
            'task_added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla added by Hugo'},
            'hugo.boss',
            {'en': None})


        resource = self.center.fetch_resource(Oguid('fd', '123'))
        self.assertEquals('fd', resource.admin_unit_id)
        self.assertEquals(123, resource.int_id)

    def test_creates_notifications_for_each_resource_watcher(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))

        resource_a = create(Builder('resource').oguid('fd:123')
                            .watchers([hugo, peter]))

        activity = self.center.add_activity(
            Oguid('fd', '123'),
            'TASK_ADDED',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task bla added'},
            {'en': 'Task bla added by Hugo'},
            'hugo.boss',
            {'en': None}).get('activity')

        notification = peter.notifications[0]
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.is_read)

        notification = hugo.notifications[0]
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.is_read)

    def test_does_not_create_an_notification_for_the_actor(self):
        peter = create(Builder('watcher').having(user_id='peter'))
        hugo = create(Builder('watcher').having(user_id='hugo'))

        create(Builder('resource').oguid('fd:123').watchers([hugo, peter]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'TASK_ADDED',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task accepted'},
            {'en': 'Task bla added by Peter'},
            'peter',
            {'en': None})


        self.assertEquals(1, len(hugo.notifications))
        self.assertEquals(0, len(peter.notifications))


class TestNotificationHandling(ActivityTestCase):

    def setUp(self):
        super(TestNotificationHandling, self).setUp()

        self.center = NotificationCenter()

        self.peter = create(Builder('watcher').having(user_id='peter'))
        self.hugo = create(Builder('watcher').having(user_id='hugo'))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.hugo, self.peter]))
        self.resource_b = create(Builder('resource')
                                 .oguid('fd:456')
                                 .watchers([self.hugo]))
        self.resource_c = create(Builder('resource')
                                 .oguid('fd:789')
                                 .watchers([self.peter]))

        self.activity_1 = self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla added by Peter'},
            'hugo.boss',
            {'en': None}).get('activity')
        self.activity_2 = self.center.add_activity(
            Oguid('fd', '123'),
            'task-transition-open-in-progress',
            {'en': 'Kennzahlen 2015 erfassen'},
            {'en': 'Task accepted'},
            {'en': 'Task bla accepted by Peter'},
            'peter.mueller',
            {'en': None}).get('activity')

        self.activity_3 = self.center.add_activity(
            Oguid('fd', '456'),
            'task-added',
            {'en': 'Besprechung Gesuch'},
            {'en': 'Task added'},
            {'en': 'Task for added by Peter'},
            'peter.mueller',
            {'en': None}).get('activity')

        self.activity_4 = self.center.add_activity(
            Oguid('fd', '789'),
            'task-added',
            {'en': 'Vorbereitung Besprechung'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Franz'},
            'franz.meier',
            {'en': None}).get('activity')

    def test_get_users_notifications_lists_only_users_notifications(self):
        peters_notifications = self.center.get_users_notifications('peter')
        hugos_notifications = self.center.get_users_notifications('hugo')

        self.assertEquals(
            [self.activity_4, self.activity_2, self.activity_1],
            [notification.activity for notification in peters_notifications])

        self.assertEquals(
            [self.activity_3, self.activity_2, self.activity_1],
            [notification.activity for notification in hugos_notifications])

    def test_get_users_notifications_only_unread_parameter(self):
        notifications = self.center.get_users_notifications('peter')
        self.center.mark_notification_as_read(notifications[0].notification_id)

        peters_notifications = self.center.get_users_notifications('peter', only_unread=True)
        self.assertEquals(2, len(peters_notifications))

    def test_get_users_notifications_retuns_empty_list_when_no_notifications_for_this_user_exists(self):
        create(Builder('watcher').having(user_id='franz'))

        self.assertEquals([],
                          self.center.get_users_notifications('franz'))

    def test_mark_notification_as_read(self):
        notification_id = self.peter.notifications[0].notification_id

        self.center.mark_notification_as_read(notification_id)

        self.assertTrue(Notification.get(notification_id).is_read)

    def test_mark_an_already_read_notification_is_ignored(self):
        notification_id = self.peter.notifications[0].notification_id

        self.center.mark_notification_as_read(notification_id)
        self.assertTrue(Notification.get(notification_id).is_read)

        self.center.mark_notification_as_read(notification_id)
        self.assertTrue(Notification.get(notification_id).is_read)

    def test_list_notifications_by_userid(self):
        notifications = self.center.list_notifications(userid='peter')
        self.assertEquals(
            [self.activity_1, self.activity_2, self.activity_4],
            [notification.activity for notification in notifications])

    def test_list_notifications_with_sorting(self):
        notifications = self.center.list_notifications(userid='peter', sort_on='kind')

        self.assertEquals(
            ['task-added', 'task-added', 'task-transition-open-in-progress'],
            [notification.activity.kind for notification in notifications])

    def test_list_notifications_with_reverse_sorting(self):
        notifications = self.center.list_notifications(
            userid='peter', sort_on='kind', sort_reverse=True)

        self.assertEquals(
            ['task-transition-open-in-progress', 'task-added', 'task-added'],
            [notification.activity.kind for notification in notifications])

    @unittest.skip('Textfilter not implemented yet')
    def test_list_notifications_with_text_filter_on_title(self):
        notifications = self.center.list_notifications(
            userid='peter', sort_on='kind', filters=['kennzahlen'])

        self.assertEquals(
            [self.activity_1, self.activity_2],
            [notification.activity for notification in notifications])

    @unittest.skip('Textfilter not implemented yet')
    def test_list_notifications_with_text_filter_on_kind(self):
        notifications = self.center.list_notifications(
            userid='peter', sort_on='kind', filters=['Task', 'added'])

        self.assertEquals(
            ['task-added', 'task-added'],
            [notification.activity.kind for notification in notifications])


class FakeDispatcher(object):

    setting_key = 'mail_notification'

    def __init__(self):
        self.notified = []

    def dispatch_notifications(self, notifications):
        for notification in notifications:
            notification.dispatch(self)

        return []

    def dispatch_notification(self, notification):
        self.notified.append(notification)


class TestDispatchers(ActivityTestCase):

    def setUp(self):
        super(TestDispatchers, self).setUp()

        self.dispatcher = FakeDispatcher()
        self.center = NotificationCenter([self.dispatcher])

        hugo = create(Builder('watcher').having(user_id='hugo'))
        peter = create(Builder('watcher').having(user_id='peter'))

        self.resource = create(Builder('resource').oguid('fd:123')
                               .watchers([hugo, peter]))

    def test_check_for_notification_default(self):
        setting = create(Builder('notification_default_setting')
                         .having(kind='task-added',
                                 mail_notification=False))

        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        self.assertEquals(0, len(self.dispatcher.notified))

        setting.mail_notification = True
        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        self.assertEquals(2, len(self.dispatcher.notified))

    def test_if_setting_for_kind_does_not_exist_dispatcher_is_ignored(self):
        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})


        self.assertEquals(0, len(self.dispatcher.notified))
