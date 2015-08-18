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
                                   .having(user_id=TEST_USER_ID))
        self.hugo = create(Builder('watcher').having(user_id='hugo'))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.hugo, self.test_watcher]))

        self.activity_a = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task accepted',
                                         created=datetime(2015, 8, 17, 9, 0, tzinfo=pytz.UTC)))
        self.activity_b = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task added',
                                         created=datetime(2015, 8, 17, 7, 0, tzinfo=pytz.UTC)))
        self.activity_c = create(Builder('activity')
                                 .having(resource=self.resource_a,
                                         summary='Task resolved',
                                         created=datetime(2015, 8, 17, 12, 0, tzinfo=pytz.UTC)))

    @browsing
    def test_header_contains_number_of_unread_messages(self, browser):
        create(Builder('notification')
               .having(activity=self.activity_a, watcher=self.test_watcher))
        create(Builder('notification')
               .having(activity=self.activity_b, watcher=self.test_watcher))
        create(Builder('notification')
               .having(activity=self.activity_c, watcher=self.test_watcher))

        browser.login().open()
        self.assertEquals(
            '3',
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
    def test_lists_only_unread_notifications(self, browser):
        create(Builder('notification')
               .having(activity=self.activity_a, watcher=self.test_watcher))
        create(Builder('notification')
               .as_read()
               .having(activity=self.activity_b, watcher=self.test_watcher))
        create(Builder('notification')
               .having(activity=self.activity_c, watcher=self.test_watcher))

        browser.login().open()

        self.assertEquals(
            ['Task resolved', 'Task accepted'],
            browser.css('.item-content .item-summary').text)

    @browsing
    def test_lists_notification_chronologic_newest_at_the_top(self, browser):
        create(Builder('notification')
               .having(activity=self.activity_a, watcher=self.test_watcher))
        create(Builder('notification')
               .having(activity=self.activity_b, watcher=self.test_watcher))
        create(Builder('notification')
               .having(activity=self.activity_c, watcher=self.test_watcher))

        browser.login().open()

        self.assertEquals(
            ['Task resolved', 'Task accepted', 'Task added'],
            browser.css('.item-content .item-summary').text)

    @browsing
    def test_notifications_is_limited_to_ten_latest(self, browser):
        for i in range(13):
            create(Builder('notification')
                   .having(activity=self.activity_a, watcher=self.test_watcher))

        browser.login().open()
        notifications = browser.css('.notification-item a.item-location')
        self.assertEquals(10, len(notifications))

    @browsing
    def test_notifications_are_linked_to_resolve_notification_view(self, browser):
        create(Builder('notification')
               .having(activity=self.activity_c, watcher=self.test_watcher))

        browser.login().open()
        link = browser.css('dl.notificationsMenu .item-content a').first
        self.assertEquals(
            'http://example.com/@@resolve_notification?notification_id=1',
            link.get('href'))

    @browsing
    def test_displays_message_when_no_unread_notifications(self, browser):
        browser.login().open()

        self.assertEquals(
            ['No unread notifications', 'All Notifications'],
            browser.css('dl.notificationsMenu li').text)

        self.assertEquals(
            'no-content',
            browser.css('dl.notificationsMenu li').first.get('class'))
