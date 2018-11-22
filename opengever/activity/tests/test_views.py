from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity.center import NotificationCenter
from opengever.activity.model import Resource
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import json
import pytz


class TestMarkAsRead(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestMarkAsRead, self).setUp()

        self.center = NotificationCenter()
        self.test_user = create(Builder('watcher')
                                .having(actorid=TEST_USER_ID))
        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.test_user]))

        with freeze(pytz.UTC.localize(datetime(2014, 5, 7, 12, 30))):
            self.activity_1 = self.center.add_activity(
                Oguid('fd', '123'),
                'task-added',
                {'en': 'Kennzahlen 2014 erfassen'},
                {'en': 'Task added'},
                {'en': 'Task bla added by Hugo'},
                'hugo.boss',
                {'en': None}).get('activity')

            self.activity_2 = self.center.add_activity(
                Oguid('fd', '123'),
                'task-transition-open-in-progress',
                {'en': 'Kennzahlen 2014 erfassen'},
                {'en': 'Task accepted'},
                {'en': 'Task bla accepted'},
                'hugo.boss',
                {'en': None}).get('activity')

            self.notifications = self.center.get_users_notifications(TEST_USER_ID)

    @browsing
    def test_mark_single_notification_as_read(self, browser):
        notification_id = self.notifications[0].notification_id
        browser.login().open(self.portal, view='notifications/read',
                             data={'notification_ids': json.dumps([notification_id])})

        notifications = self.center.get_users_notifications(TEST_USER_ID)
        self.assertTrue(notifications[0].is_read)
        self.assertFalse(notifications[1].is_read)

    @browsing
    def test_mark_multiple_notifications_as_read(self, browser):
        ids = [self.notifications[0].notification_id,
               self.notifications[1].notification_id]

        browser.login().open(self.portal, view='notifications/read',
                             data={'notification_ids': json.dumps(ids)})

        notifications = self.center.get_users_notifications(TEST_USER_ID)
        self.assertTrue(notifications[0].is_read)
        self.assertTrue(notifications[1].is_read)

    @browsing
    def test_mark_already_read_or_invalid_notification_as_read_is_ignored(self, browser):
        invalid = 123
        notification_id = self.notifications[0].notification_id

        self.notifications[0].is_read = True

        browser.login().open(
            self.portal, view='notifications/read',
            data={'notification_ids': json.dumps([invalid, notification_id])})

    @browsing
    def test_read_raise_exception_when_parameter_is_missing(self, browser):
        with browser.expect_http_error():
            browser.login().open(self.portal, view='notifications/read')


class TestListNotifications(FunctionalTestCase):

    def setUp(self):
        super(TestListNotifications, self).setUp()
        self.center = NotificationCenter()
        self.test_user = create(Builder('watcher')
                                .having(actorid=TEST_USER_ID))
        self.resource_a = create(Builder('resource')
                                 .oguid('admin-unit-1:123')
                                 .watchers([self.test_user]))

        created = pytz.UTC.localize(datetime(2014, 5, 7, 12, 30))
        self.activity = create(Builder('activity')
                               .having(resource=self.resource_a,
                                       created=created,
                                       actor_id='hugo.boss',
                                       kind='task-added',
                                       title=u'Kennzahlen 2014 erfassen',
                                       label=u'Task added',
                                       summary=u'Task bla added by Hugo'))

    @browsing
    def test_returns_a_json_representation_of_the_notifications(self, browser):
        create(Builder('notification')
               .having(activity=self.activity, userid=TEST_USER_ID, is_read=False))
        create(Builder('notification')
               .having(activity=self.activity, userid=TEST_USER_ID, is_read=True))

        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(
            [{u'title': u'Kennzahlen 2014 erfassen',
              u'read': False,
              u'created': u'2014-05-07T12:30:00+00:00',
              u'summary': u'Task bla added by Hugo',
              u'target': u'_self',
              u'link': u'http://example.com/@@resolve_notification?notification_id=1',
              u'label': u'Task added',
              u'id': 1},
             {u'title': u'Kennzahlen 2014 erfassen',
              u'read': True,
              u'created': u'2014-05-07T12:30:00+00:00',
              u'summary': u'Task bla added by Hugo',
              u'target': u'_self',
              u'link': u'http://example.com/@@resolve_notification?notification_id=2',
              u'label': u'Task added',
              u'id': 2}], browser.json.get('notifications'))

    @browsing
    def test_link_target_depends_on_resource_location(self, browser):
        create(Builder('notification')
               .having(activity=self.activity, userid=TEST_USER_ID, is_read=False))

        # on current admin unit
        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(
            u'_self', browser.json.get('notifications')[0]['target'])

        Resource.query.first().admin_unit_id = 'fd'
        from opengever.base.model import create_session
        create_session().flush()

        # on forreign admin unit
        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(
            u'_blank', browser.json.get('notifications')[0]['target'])

    @browsing
    def test_is_batched_in_tens_by_default(self, browser):
        for i in range(0, 15):
            create(Builder('notification')
                   .having(activity=self.activity,
                           userid=TEST_USER_ID,
                           is_read=False))

        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(10, len(browser.json.get('notifications')))

    @browsing
    def test_batchsize_can_be_set_by_request_parameter(self, browser):
        for i in range(0, 15):
            create(Builder('notification')
                   .having(activity=self.activity,
                           userid=TEST_USER_ID,
                           is_read=False))

        browser.login().open(self.portal, view="notifications/list",
                             data={'batch_size': 12})
        self.assertEquals(12, len(browser.json.get('notifications')))

    @browsing
    def test_page_can_be_set_by_request_parameter(self, browser):
        for i in range(0, 17):
            create(Builder('notification')
                   .having(activity=self.activity,
                           userid=TEST_USER_ID,
                           is_read=False))

        # first page
        browser.login().open(self.portal, view="notifications/list",
                             data={'batch_size': 7})
        self.assertEquals(
            [1, 2, 3, 4, 5, 6, 7],
            [item['id'] for item in browser.json.get('notifications')])

        # second page
        browser.login().open(self.portal, view="notifications/list",
                             data={'batch_size': 7, 'page': 2})
        self.assertEquals(
            [8, 9, 10, 11, 12, 13, 14],
            [item['id'] for item in browser.json.get('notifications')])

        # third page
        browser.login().open(self.portal, view="notifications/list",
                             data={'batch_size': 7, 'page': 3})
        self.assertEquals(
            [15, 16, 17],
            [item['id'] for item in browser.json.get('notifications')])

    @browsing
    def test_next_page_url(self, browser):
        for i in range(0, 17):
            create(Builder('notification')
                   .having(activity=self.activity,
                           userid=TEST_USER_ID,
                           is_read=False))

        browser.login().open(self.portal, view="notifications/list",
                             data={'batch_size': 7})

        next_page = browser.json.get('next_page')
        browser.open(next_page)
        self.assertEquals(
            [8, 9, 10, 11, 12, 13, 14],
            [item['id'] for item in browser.json.get('notifications')])

    @browsing
    def test_next_page_url_is_empty_when_next_page_does_not_exist(self, browser):
        for i in range(0, 17):
            create(Builder('notification')
                   .having(activity=self.activity,
                           userid=TEST_USER_ID,
                           is_read=False))

        browser.login().open(self.portal,
                             view="notifications/list",
                             data={'batch_size': 7, 'page': 2})
        self.assertEquals(
            u'http://nohost/plone/notifications/list?page=3&batch_size=7',
            browser.json.get('next_page'))

        browser.login().open(self.portal,
                             view="notifications/list",
                             data={'batch_size': 7, 'page': 3})
        self.assertEquals(None, browser.json.get('next_page'))

    @browsing
    def test_lists_notification_chronologic_newest_at_the_top(self, browser):
        created = pytz.UTC.localize(datetime(2015, 5, 7, 12, 30))
        newes = create(Builder('activity')
                       .having(resource=self.resource_a,
                               created=created,
                               actor_id='hugo.boss',
                               kind='task-added',
                               title=u'Kennzahlen 2015 erfassen',
                               label=u'Task added',
                               summary=u'Task bla added by Hugo'))

        create(Builder('notification')
               .having(activity=self.activity,
                       userid=TEST_USER_ID, is_read=False))
        create(Builder('notification')
               .having(activity=newes,
                       userid=TEST_USER_ID, is_read=False))

        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(u'Kennzahlen 2015 erfassen',
                          browser.json.get('notifications')[0].get('title'))

    @browsing
    def test_lists_only_notification_with_badge_enabled(self, browser):
        created = pytz.UTC.localize(datetime(2015, 5, 7, 12, 30))
        task_added = create(Builder('activity')
                            .having(resource=self.resource_a,
                                    created=created,
                                    actor_id='hugo.boss',
                                    kind='task-added',
                                    title=u'Kennzahlen 2015 erfassen',
                                    label=u'Task added',
                                    summary=u'Task bla added by Hugo'))

        create(Builder('notification')
               .having(activity=self.activity,
                       userid=TEST_USER_ID, is_read=False, is_badge=False))

        create(Builder('notification')
               .having(activity=task_added,
                       userid=TEST_USER_ID, is_read=False, is_badge=True))

        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(1, len(browser.json.get('notifications')))
        self.assertEquals(u'Kennzahlen 2015 erfassen',
                          browser.json.get('notifications')[0].get('title'))

    @browsing
    def test_notifications_are_linked_to_resolve_notification_view(self, browser):
        create(Builder('notification')
               .having(activity=self.activity,
                       userid=TEST_USER_ID, is_read=False))

        browser.login().open(self.portal, view="notifications/list")
        self.assertEquals(
            'http://example.com/@@resolve_notification?notification_id=1',
            browser.json.get('notifications')[0].get('link'))
