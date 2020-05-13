from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity.center import NotificationCenter
from opengever.activity.model import Resource
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from time import time
import pytz


FREEZE_TIME = datetime(2014, 5, 7, 12, 30, 0, tzinfo=pytz.UTC)


FREEZE_TIME_BEFORE = datetime(2014, 5, 7, 13, 30, 0, tzinfo=pytz.UTC)
FREEZE_TIME_FIRST = datetime(2014, 5, 7, 14, 30, 0, tzinfo=pytz.UTC)
FREEZE_TIME_BETWEEN = datetime(2014, 5, 7, 15, 30, 0, tzinfo=pytz.UTC)
FREEZE_TIME_SECOND = datetime(2014, 5, 7, 16, 30, 0, tzinfo=pytz.UTC)


class TestMarkAsRead(IntegrationTestCase):

    def setUp(self):
        super(TestMarkAsRead, self).setUp()
        with self.login(self.regular_user):
            self.center = NotificationCenter()
            self.resource = Resource.query.get_by_oguid(Oguid.for_object(self.task))

            # XXX - something is wonky with the builder for activities
            with freeze(FREEZE_TIME_FIRST):
                self.activity_1 = create(
                    Builder('activity')
                    .having(resource=self.resource, created=FREEZE_TIME_FIRST)
                )
                create(
                    Builder('notification')
                    .id(1)
                    .having(
                        activity=self.activity_1,
                        userid=self.regular_user.id,
                    )
                )

            # XXX - something is wonky with the builder for activities
            with freeze(FREEZE_TIME_SECOND):
                self.activity_2 = create(
                    Builder('activity')
                    .having(resource=self.resource, created=FREEZE_TIME_SECOND)
                )
                create(
                    Builder('notification')
                    .id(2)
                    .having(
                        activity=self.activity_2,
                        userid=self.regular_user.id,
                    )
                )

            self.notifications = self.center.get_users_notifications(
                self.regular_user.id)

    @browsing
    def test_mark_all_notifications_as_read(self, browser):
        self.login(self.regular_user, browser)
        # Now is always after both FREEZE_TIME_FIRST and FREEZE_TIME_SECOND
        browser.open(view='notifications/read', data={'timestamp': int(time())})

        notifications = self.center.get_users_notifications(
            self.regular_user.id)
        self.assertTrue(notifications[0].is_read)
        self.assertTrue(notifications[1].is_read)

    @browsing
    def test_mark_some_notifications_as_read(self, browser):
        self.login(self.regular_user, browser)
        # This is testing a race condition of more notifications after render
        with freeze(FREEZE_TIME_BETWEEN):
            browser.open(
                view='notifications/read', data={'timestamp': int(time())})

        notifications = self.center.get_users_notifications(
            self.regular_user.id)
        self.assertFalse(notifications[0].is_read)
        self.assertTrue(notifications[1].is_read)

    @browsing
    def test_mark_no_notifications_as_read(self, browser):
        self.login(self.regular_user, browser)
        # This is testing a race condition of more notifications after render
        with freeze(FREEZE_TIME_BEFORE):
            browser.open(
                view='notifications/read', data={'timestamp': int(time())})

        notifications = self.center.get_users_notifications(
            self.regular_user.id)
        self.assertFalse(notifications[0].is_read)
        self.assertFalse(notifications[1].is_read)

    @browsing
    def test_read_raise_exception_when_parameter_is_missing(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error():
            browser.open(self.portal, view='notifications/read')


class TestListNotifications(IntegrationTestCase):

    def setUp(self):
        super(TestListNotifications, self).setUp()
        with self.login(self.regular_user), freeze(FREEZE_TIME):
            self.center = NotificationCenter()
            self.resource = Resource.query.get_by_oguid(Oguid.for_object(self.task))

            self.activity = create(
                Builder('activity')
                .having(resource=self.resource, created=FREEZE_TIME)
            )

    @browsing
    def test_returns_a_json_representation_of_the_notifications(self, browser):
        self.login(self.regular_user, browser)
        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=False,
            )
        )
        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=True,
            )
        )

        browser.open(view="notifications/list")
        expected_notifications = [
            {
                u'created': u'2014-05-07T12:30:00+00:00',
                u'id': 1,
                u'label': None,
                u'link': u'http://nohost/plone/@@resolve_notification'
                         u'?notification_id=1',
                u'read': False,
                u'summary': u'Task created by Test User',
                u'target': u'_self',
                u'title': u'Kennzahlen 2014 erfassen',
            },
            {
                u'created': u'2014-05-07T12:30:00+00:00',
                u'id': 2,
                u'label': None,
                u'link': u'http://nohost/plone/@@resolve_notification'
                         u'?notification_id=2',
                u'read': True,
                u'summary': u'Task created by Test User',
                u'target': u'_self',
                u'title': u'Kennzahlen 2014 erfassen',
            },
        ]
        self.assertEqual(
            expected_notifications, browser.json.get('notifications'))

    @browsing
    def test_link_target_depends_on_resource_location(self, browser):
        self.login(self.regular_user, browser)
        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=False,
            )
        )

        # On current admin unit - 'plone'
        browser.open(view="notifications/list")
        target = browser.json.get('notifications')[0]['target']
        self.assertEqual(u'_self', target)

        # On foreign admin unit - 'fd'
        Resource.query.get_by_oguid(self.task.oguid).admin_unit_id = 'fd'
        browser.open(view="notifications/list")

        target = browser.json.get('notifications')[0]['target']
        self.assertEqual(u'_blank', target)

    @browsing
    def test_is_batched_in_tens_by_default(self, browser):
        self.login(self.regular_user, browser)
        for _ in range(0, 15):
            create(
                Builder('notification')
                .having(
                    activity=self.activity,
                    userid=self.regular_user.id,
                    is_read=False,
                )
            )

        browser.open(view="notifications/list")
        self.assertEqual(10, len(browser.json.get('notifications')))

    @browsing
    def test_batchsize_can_be_set_by_request_parameter(self, browser):
        self.login(self.regular_user, browser)
        for _ in range(0, 15):
            create(
                Builder('notification')
                .having(
                    activity=self.activity,
                    userid=self.regular_user.id,
                    is_read=False,
                )
            )

        browser.open(view="notifications/list", data={'batch_size': 12})
        self.assertEqual(12, len(browser.json.get('notifications')))

    @browsing
    def test_page_can_be_set_by_request_parameter(self, browser):
        self.login(self.regular_user, browser)
        for _ in range(0, 17):
            create(
                Builder('notification')
                .having(
                    activity=self.activity,
                    userid=self.regular_user.id,
                    is_read=False,
                )
            )

        # first page
        browser.open(view="notifications/list", data={'batch_size': 7})
        expected_ids = [1, 2, 3, 4, 5, 6, 7]
        ids = [item['id'] for item in browser.json.get('notifications')]
        self.assertEqual(expected_ids, ids)

        # second page
        browser.open(
            view="notifications/list", data={'batch_size': 7, 'page': 2})
        expected_ids = [8, 9, 10, 11, 12, 13, 14]
        ids = [item['id'] for item in browser.json.get('notifications')]
        self.assertEqual(expected_ids, ids)

        # third page
        browser.open(
            view="notifications/list", data={'batch_size': 7, 'page': 3})
        expected_ids = [15, 16, 17]
        ids = [item['id'] for item in browser.json.get('notifications')]
        self.assertEqual(expected_ids, ids)

    @browsing
    def test_next_page_url(self, browser):
        self.login(self.regular_user, browser)
        for _ in range(0, 17):
            create(
                Builder('notification')
                .having(
                    activity=self.activity,
                    userid=self.regular_user.id,
                    is_read=False,
                ),
            )

        browser.open(view="notifications/list", data={'batch_size': 7})

        next_page = browser.json.get('next_page')
        browser.open(next_page)
        expected_ids = [8, 9, 10, 11, 12, 13, 14]
        ids = [item['id'] for item in browser.json.get('notifications')]
        self.assertEqual(expected_ids, ids)

    @browsing
    def test_next_page_url_is_empty_when_next_page_does_not_exist(self, browser):
        self.login(self.regular_user, browser)
        for _ in range(0, 17):
            create(
                Builder('notification')
                .having(
                    activity=self.activity,
                    userid=self.regular_user.id,
                    is_read=False,
                )
            )

        browser.open(
            view="notifications/list", data={'batch_size': 7, 'page': 2})
        self.assertEqual(
            u'http://nohost/plone/notifications/list?page=3&batch_size=7',
            browser.json.get('next_page'),
        )

        browser.open(
            view="notifications/list", data={'batch_size': 7, 'page': 3})
        self.assertEqual(None, browser.json.get('next_page'))

    @browsing
    def test_lists_notification_chronologic_newest_at_the_top(self, browser):
        self.login(self.regular_user, browser)
        new_activity = create(
            Builder('activity')
            .having(
                created=FREEZE_TIME,
                resource=self.resource,
                actor_id=self.regular_user.id,
                kind='task-added',
                title=u'Kennzahlen 2015 erfassen',
                label=u'Task added',
                summary=u'Task bla added by Hugo',
            )
        )
        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=False,
            )
        )
        create(
            Builder('notification')
            .having(
                activity=new_activity,
                userid=self.regular_user.id,
                is_read=False,
            )
        )

        browser.open(view="notifications/list")
        expected_notifications = [
            {
                u'created': u'2014-05-07T12:30:00+00:00',
                u'id': 1,
                u'label': None,
                u'link': u'http://nohost/plone/@@resolve_notification'
                         u'?notification_id=1',
                u'read': False,
                u'summary': u'Task created by Test User',
                u'target': u'_self',
                u'title': u'Kennzahlen 2014 erfassen',
            },
            {
                u'created': u'2014-05-07T12:30:00+00:00',
                u'id': 2,
                u'label': u'Task added',
                u'link': u'http://nohost/plone/@@resolve_notification'
                         u'?notification_id=2',
                u'read': False,
                u'summary': u'Task bla added by Hugo',
                u'target': u'_self',
                u'title': u'Kennzahlen 2015 erfassen',
            },
        ]
        self.assertEqual(
            expected_notifications, browser.json.get('notifications'))

    @browsing
    def test_lists_only_notification_with_badge_enabled(self, browser):
        self.login(self.regular_user, browser)
        task_added = create(
            Builder('activity')
            .having(
                created=FREEZE_TIME,
                resource=self.resource,
                actor_id=self.regular_user.id,
                kind='task-added',
                title=u'Kennzahlen 2015 erfassen',
                label=u'Task added',
                summary=u'Task bla added by Hugo',
            )
        )

        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=False,
                is_badge=False,
            )
        )

        create(
            Builder('notification')
            .having(
                activity=task_added,
                userid=self.regular_user.id,
                is_read=False,
                is_badge=True,
            )
        )

        browser.open(view="notifications/list")
        self.assertEqual(1, len(browser.json.get('notifications')))
        expected_notifications = [{
            u'created': u'2014-05-07T12:30:00+00:00',
            u'id': 2,
            u'label': u'Task added',
            u'link': u'http://nohost/plone/@@resolve_notification'
                     u'?notification_id=2',
            u'read': False,
            u'summary': u'Task bla added by Hugo',
            u'target': u'_self',
            u'title': u'Kennzahlen 2015 erfassen',
        }]
        self.assertEqual(
            expected_notifications, browser.json.get('notifications'))

    @browsing
    def test_notifications_are_linked_to_resolve_notification_view(self, browser):
        self.login(self.regular_user, browser)
        create(
            Builder('notification')
            .having(
                activity=self.activity,
                userid=self.regular_user.id,
                is_read=False,
            )
        )

        browser.open(self.portal, view="notifications/list")
        self.assertEqual(
            'http://nohost/plone/@@resolve_notification?notification_id=1',
            browser.json.get('notifications')[0].get('link'),
        )
