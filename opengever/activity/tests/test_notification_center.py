from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.badge import BadgeIconDispatcher
from opengever.activity.center import NotificationCenter
from opengever.activity.digest import DigestDispatcher
from opengever.activity.mail import NotificationDispatcher
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.activity.model import Subscription
from opengever.activity.model import Watcher
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.tests.base import ActivityTestCase
from opengever.base.oguid import Oguid
from opengever.ogds.models.user_settings import UserSettings
from sqlalchemy.exc import IntegrityError
import transaction
import unittest


class TestResourceHandling(ActivityTestCase):

    def setUp(self):
        super(TestResourceHandling, self).setUp()
        self.center = NotificationCenter()

    def test_add_watcher_to_a_resource(self):
        hugo = create(Builder('watcher').having(actorid='hugo'))
        create(Builder('watcher').having(actorid='peter'))
        res = create(Builder('resource').oguid('fd:1234'))

        res.add_watcher('hugo', TASK_ISSUER_ROLE)
        self.assertEquals([hugo], res.watchers)

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

    def test_fetch_returns_watcher_by_means_of_actor_id(self):
        hugo = create(Builder('watcher').having(actorid='hugo'))
        peter = create(Builder('watcher').having(actorid='peter'))

        self.assertEquals(hugo, self.center.fetch_watcher('hugo'))
        self.assertEquals(peter, self.center.fetch_watcher('peter'))

    def test_return_none_when_watcher_not_exists(self):
        self.assertEquals(None, self.center.fetch_watcher('peter'))

    def test_adding(self):
        self.center.add_watcher('peter')

        self.assertEquals(1, len(Watcher.query.all()))
        self.assertEquals('peter', Watcher.query.first().actorid)

    def test_add_watcher_twice_raise_integrity_error(self):
        self.center.add_watcher('peter')
        with self.assertRaises(IntegrityError):
            self.center.add_watcher('peter')
            transaction.commit()

        transaction.abort()

    def test_add_watcher_to_resource(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(
            Oguid('fd', '123'), 'peter', omit_watcher_added_event=True)

        self.assertEquals([peter], list(resource.watchers))

    def test_adding_watcher_twice_to_resource_is_ignored(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(
            Oguid('fd', '123'), 'peter', omit_watcher_added_event=True)
        self.center.add_watcher_to_resource(
            Oguid('fd', '123'), 'peter', omit_watcher_added_event=True)

        self.assertEquals([peter], list(resource.watchers))

    def test_add_watcher_to_resource_creates_resource_when_not_exists(self):
        peter = create(Builder('watcher').having(actorid='peter'))

        self.center.add_watcher_to_resource(
            Oguid('fd', '123'), 'peter', omit_watcher_added_event=True)

        resource = peter.resources[0]
        self.assertEquals('fd:123', resource.oguid)

    def test_add_watcher_to_resource_creates_watcher_when_not_exists(self):
        resource = create(Builder('resource').oguid('fd:123'))

        self.center.add_watcher_to_resource(
            Oguid('fd', '123'), 'peter', omit_watcher_added_event=True)

        watcher = list(resource.watchers)[0]
        self.assertEquals('peter', watcher.actorid)

    def test_get_watchers_returns_a_list_of_resource_watchers(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        hugo = create(Builder('watcher').having(actorid='hugo'))
        fritz = create(Builder('watcher').having(actorid='fritz'))

        resource_1 = create(Builder('resource')
                            .oguid('fd:123').watchers([hugo, fritz]))
        resource_2 = create(Builder('resource')
                            .oguid('fd:456').watchers([peter]))

        # A weakref gets reaped unless we keep a reference to the resources.
        # https://stackoverflow.com/questions/30044069/stale-association-proxy-parent-object-has-gone-out-of-scope-with-flask-sqlalc
        # So to squelch pyflakes we do trivial asserts on them here.
        self.assertEquals(123, resource_1.int_id)
        self.assertEquals(456, resource_2.int_id)

        self.assertEquals((hugo, fritz), self.center.get_watchers(Oguid('fd', '123')))
        self.assertEquals((peter,),
                          self.center.get_watchers(Oguid('fd', '456')))

    def test_get_watchers_returns_empty_list_when_resource_not_exists(self):
        self.assertEquals((), self.center.get_watchers(Oguid('fd', '123')))

    def test_remove_watcher_from_resource_will_be_ignored_when_watcher_not_exists(self):
        create(Builder('resource').oguid('fd:123'))

        self.center.remove_watcher_from_resource(
            Oguid('fd', '123'), 'peter', WATCHER_ROLE)

    def test_remove_watcher_from_resource_will_remove_subscription_if_no_roles_left(self):
        resource = create(Builder('resource').oguid('fd:123'))
        watcher = create(Builder('watcher').having(actorid=u'peter'))
        create(Builder('subscription')
               .having(resource=resource, watcher=watcher, role=WATCHER_ROLE))

        self.center.remove_watcher_from_resource(
            Oguid('fd', '123'), 'peter', WATCHER_ROLE)

        self.assertEquals([], resource.watchers)

    def test_remove_watcher_from_resource_will_be_ignored_when_resource_not_exists(self):
        create(Builder('watcher').having(actorid='peter'))

        self.center.remove_watcher_from_resource(
            Oguid('fd', '123'), 'peter', WATCHER_ROLE)

    def test_remove_watcher_from_resource(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        hugo = create(Builder('watcher').having(actorid='hugo'))
        resource = create(Builder('resource')
                          .oguid('fd:123')
                          .watchers([hugo, peter]))

        self.center.remove_watcher_from_resource(
            Oguid('fd', '123'), 'peter', WATCHER_ROLE)

        self.assertEquals([hugo], resource.watchers)

    def test_remove_watchers_from_resource_by_role(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        hugo = create(Builder('watcher').having(actorid='hugo'))
        marie = create(Builder('watcher').having(actorid='marie'))
        resource = create(Builder('resource').oguid('fd:123'))
        create(Builder('subscription')
               .having(resource=resource, watcher=peter, role=WATCHER_ROLE))
        create(Builder('subscription')
               .having(resource=resource, watcher=marie, role=WATCHER_ROLE))
        create(Builder('subscription')
               .having(resource=resource, watcher=peter, role=TASK_ISSUER_ROLE))
        create(Builder('subscription')
               .having(resource=resource, watcher=hugo, role=TASK_ISSUER_ROLE))

        self.center.remove_watchers_from_resource_by_role(
            Oguid('fd', '123'), WATCHER_ROLE)

        self.assertEqual(
            set([TASK_ISSUER_ROLE]),
            set([subscription.role for subscription in Subscription.query.all()]))

        self.assertEquals([peter, hugo], resource.watchers)

    def test_remove_watchers_from_resource_by_role_does_not_affect_other_resources(self):
        hugo = create(Builder('watcher').having(actorid='hugo'))

        create(Builder('resource').oguid('fd:123').watchers([hugo]))
        create(Builder('resource').oguid('fd:234').watchers([hugo]))

        self.assertEqual(2, Subscription.query.count())
        self.assertEqual(
            ['fd:123', 'fd:234'],
            [subscription.resource.oguid.id for subscription in Subscription.query.all()])

        self.center.remove_watchers_from_resource_by_role(
            Oguid('fd', '234'), WATCHER_ROLE)


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
        peter = create(Builder('watcher').having(actorid='peter'))
        hugo = create(Builder('watcher').having(actorid='hugo'))

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

        notification = Notification.query.by_user('peter').first()
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.is_read)

        notification = Notification.query.by_user('hugo').first()
        self.assertEquals(activity, notification.activity)
        self.assertEquals(resource_a, notification.activity.resource)
        self.assertFalse(notification.is_read)

    def test_only_creates_notifications_for_specific_users(self):
        peter = create(Builder('watcher').having(actorid='peter'))
        hugo = create(Builder('watcher').having(actorid='hugo'))
        nadja = create(Builder('watcher').having(actorid='nadja'))

        create(Builder('resource').oguid('fd:123').watchers([hugo, peter, nadja]))
        activity = self.center.add_activity(
            Oguid('fd', '123'),
            'TASK_ADDED',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task bla added'},
            {'en': 'Task bla added by Hugo'},
            'hugo.boss',
            {'en': None},
            notification_recipients=[peter, nadja]).get('activity')

        self.assertEqual(2, len(activity.notifications))
        self.assertEqual(['peter', 'nadja'],
                         [notification.userid.actorid for notification in activity.notifications])

    def test_does_not_create_notification_for_actor_if_notify_own_actions_disabled(self):
        create(Builder('ogds_user').id('peter'))
        peter = create(Builder('watcher').having(actorid='peter'))
        create(Builder('ogds_user').id('hugo'))
        hugo = create(Builder('watcher').having(actorid='hugo'))

        self.assertFalse(UserSettings.get_setting_for_user(
            'peter', 'notify_own_actions'))

        create(Builder('resource').oguid('fd:123').watchers([hugo, peter]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'TASK_ADDED',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task accepted'},
            {'en': 'Task bla added by Peter'},
            'peter',
            {'en': None})

        self.assertEquals(1, Notification.query.by_user('hugo').count())
        self.assertEquals(0, Notification.query.by_user('peter').count())

    def test_creates_notification_for_actor_if_notify_own_actions_enabled(self):
        create(Builder('ogds_user').id('peter'))
        peter = create(Builder('watcher').having(actorid='peter'))
        create(Builder('ogds_user').id('hugo'))
        hugo = create(Builder('watcher').having(actorid='hugo'))

        UserSettings.save_setting_for_user(
            'peter', 'notify_own_actions', True)

        create(Builder('resource').oguid('fd:123').watchers([hugo, peter]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'TASK_ADDED',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task accepted'},
            {'en': 'Task bla added by Peter'},
            'peter',
            {'en': None})

        self.assertEquals(1, Notification.query.by_user('hugo').count())
        self.assertEquals(1, Notification.query.by_user('peter').count())


class TestNotificationHandling(ActivityTestCase):

    def setUp(self):
        super(TestNotificationHandling, self).setUp()

        self.center = NotificationCenter()

        self.peter = create(Builder('ogds_user').id('peter'))
        self.peter = create(Builder('watcher').having(actorid='peter'))
        self.hugo = create(Builder('ogds_user').id('hugo'))
        self.hugo = create(Builder('watcher').having(actorid='hugo'))

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
        create(Builder('watcher').having(actorid='franz'))

        self.assertEquals([],
                          self.center.get_users_notifications('franz'))

    def test_mark_notification_as_read(self):
        notification = Notification.query.by_user('peter').first()
        self.center.mark_notification_as_read(notification.notification_id)
        self.assertTrue(Notification.get(notification.notification_id).is_read)

    def test_mark_notifications_as_read(self):
        notification_1, notification_2, notification_3 = Notification.query.by_user(
            'peter').all()

        self.center.mark_notifications_as_read(
            [notification_1.notification_id, notification_3.notification_id])

        self.assertTrue(notification_1.is_read)
        self.assertFalse(notification_2.is_read)
        self.assertTrue(notification_3.is_read)

    def test_mark_an_already_read_notification_is_ignored(self):
        notification = Notification.query.by_user('peter').first()
        notification_id = notification.notification_id

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


class FakeMailDispatcher(NotificationDispatcher):

    roles_key = 'mail_notification_roles'

    def __init__(self):
        self.notified = []

    def dispatch_notification(self, notification):
        self.notified.append(notification)


class TestDispatchers(ActivityTestCase):

    def setUp(self):
        super(TestDispatchers, self).setUp()

        self.dispatcher = FakeMailDispatcher()
        self.center = NotificationCenter(
            [self.dispatcher, BadgeIconDispatcher(), DigestDispatcher()])

        hugo = create(Builder('watcher').having(actorid='hugo'))
        peter = create(Builder('watcher').having(actorid='peter'))
        resource = create(Builder('resource').oguid('fd:123'))
        create(Builder('subscription')
               .having(resource=resource, watcher=hugo, role=WATCHER_ROLE))
        create(Builder('subscription')
               .having(resource=resource,
                       watcher=peter,
                       role=TASK_RESPONSIBLE_ROLE))

    def test_uses_personal_setting_if_exists(self):
        create(Builder('notification_default_setting')
               .having(kind='task-added-or-reassigned',
                       mail_notification_roles=[WATCHER_ROLE,
                                                TASK_RESPONSIBLE_ROLE]))

        create(Builder('notification_setting')
               .having(kind='task-added-or-reassigned', userid='hugo'))


        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        self.assertEquals(1, len(self.dispatcher.notified))
        self.assertEquals(
            ['peter'],
            [note.userid for note in self.dispatcher.notified])

    def test_uses_notification_default_as_fallback(self):
        setting = create(Builder('notification_default_setting')
                         .having(kind='task-added-or-reassigned',
                                 mail_notification_roles=[
                                     WATCHER_ROLE, TASK_RESPONSIBLE_ROLE]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        self.assertEquals(2, len(self.dispatcher.notified))

    def test_only_watchers_with_configured_roles_are_dispatched(self):
        setting = create(Builder('notification_default_setting')
                         .having(kind='task-added-or-reassigned',
                                 mail_notification_roles=[WATCHER_ROLE]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        self.assertEquals(1, len(self.dispatcher.notified))
        self.assertEquals(u'hugo', self.dispatcher.notified[0].userid)

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

    def test_badge_dispatcher_sets_badge_flag_depending_on_the_setting(self):
        setting = create(Builder('notification_default_setting')
                         .having(kind='task-added-or-reassigned',
                                 badge_notification_roles=[TASK_RESPONSIBLE_ROLE]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        peters_note = Notification.query.filter_by(userid='peter').one()
        hugos_note = Notification.query.filter_by(userid='hugo').one()

        self.assertFalse(hugos_note.is_badge)
        self.assertTrue(peters_note.is_badge)

    def test_digest_dispatcher_sets_digest_flag_depending_on_the_setting(self):
        create(Builder('notification_default_setting')
               .having(kind='task-added-or-reassigned',
                       digest_notification_roles=[TASK_RESPONSIBLE_ROLE]))

        self.center.add_activity(
            Oguid('fd', '123'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task bla accepted by Peter'},
            'hugo.boss',
            {'en': None})

        peters_note = Notification.query.filter_by(userid='peter').one()
        hugos_note = Notification.query.filter_by(userid='hugo').one()

        self.assertFalse(hugos_note.is_digest)
        self.assertTrue(peters_note.is_digest)
