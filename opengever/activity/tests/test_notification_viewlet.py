from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import pytz


class TestViewletAvailability(FunctionalTestCase):

    @browsing
    def test_is_not_available_when_activity_feature_is_disabled(self, browser):
        browser.login().open(self.portal)

        self.assertEquals([],
                          browser.css('#portal-notifications'))


class TestNotificationViewlet(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestNotificationViewlet, self).setUp()
        self.test_watcher = create(Builder('watcher')
                                   .having(actorid=TEST_USER_ID))
        self.hugo = create(Builder('watcher').having(actorid='hugo'))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.hugo, self.test_watcher]))

        self.activity_a = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task accepted',
                                         created=pytz.UTC.localize(datetime(2015, 8, 17, 9, 0))))
        self.activity_b = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task added',
                                         created=pytz.UTC.localize(datetime(2015, 8, 17, 7, 0))))
        self.activity_c = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task resolved',
                                         created=pytz.UTC.localize(datetime(2015, 8, 17, 12, 0))))

    @browsing
    def test_header_contains_number_of_unread_messages(self, browser):
        create(Builder('notification')
               .watcher(self.test_watcher)
               .having(activity=self.activity_a))
        create(Builder('notification')
               .watcher(self.test_watcher)
               .having(activity=self.activity_b))
        create(Builder('notification')
               .watcher(self.test_watcher)
               .having(activity=self.activity_c))

        browser.login().open()
        self.assertEquals(
            '3',
            browser.css('#portal-notifications .unread_number').first.text)

    @browsing
    def test_number_of_unread_messages_counts_only_badge_notifications(self, browser):
        create(Builder('notification')
               .watcher(self.test_watcher)
               .having(activity=self.activity_a))
        create(Builder('notification')
               .watcher(self.test_watcher)
               .having(activity=self.activity_b, is_badge=False))

        browser.login().open()
        self.assertEquals(
            '1',
            browser.css('#portal-notifications .unread_number').first.text)

    @browsing
    def test_number_of_unread_messages_is_not_display_when_its_0(self, browser):
        browser.login().open()
        self.assertEquals([], browser.css('#portal-notifications .num-unread'))

    @browsing
    def test_read_url(self, browser):
        browser.login().open()
        self.assertEquals(
            'http://nohost/plone/notifications/read',
            browser.css('dl.notificationsMenu').first.get('data-read-url'))

    @browsing
    def test_list_url(self, browser):
        browser.login().open()
        self.assertEquals(
            'http://nohost/plone/notifications/list',
            browser.css('dl.notificationsMenu').first.get('data-list-url'))
