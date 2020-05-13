from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Watcher
from opengever.testing import IntegrationTestCase
import pytz


class TestNotificationViewletAvailability(IntegrationTestCase):

    @browsing
    def test_is_not_available_when_activity_feature_is_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal)
        self.assertEquals([], browser.css('#portal-notifications'))


class TestNotificationViewlet(IntegrationTestCase):

    features = (
        'activity',
    )

    def setUp(self):
        super(TestNotificationViewlet, self).setUp()
        self.regular_watcher = Watcher.query.get_by_actorid(self.regular_user.id)
        self.dossier_responsible_watcher = Watcher.query.get_by_actorid(self.dossier_responsible.id)
        self.resource_a = create(
            Builder('resource')
            .oguid('fd:123')
            .watchers([self.dossier_responsible_watcher, self.regular_watcher]),
        )
        utc = pytz.timezone('Etc/UTC')
        self.activity_a = create(
            Builder('activity')
            .having(resource=self.resource_a, summary='Task accepted', created=utc.localize(datetime(2015, 8, 17, 9, 0))),
        )
        self.activity_b = create(
            Builder('activity')
            .having(resource=self.resource_a, summary='Task added', created=utc.localize(datetime(2015, 8, 17, 7, 0))),
        )
        self.activity_c = create(
            Builder('activity')
            .having(resource=self.resource_a, summary='Task resolved', created=utc.localize(datetime(2015, 8, 17, 12, 0))),
        )

    @browsing
    def test_header_contains_number_of_unread_messages(self, browser):
        self.login(self.dossier_responsible, browser)
        create(Builder('notification').watcher(self.dossier_responsible_watcher).having(activity=self.activity_a))
        create(Builder('notification').watcher(self.dossier_responsible_watcher).having(activity=self.activity_b))
        create(Builder('notification').watcher(self.dossier_responsible_watcher).having(activity=self.activity_c))
        browser.open()
        self.assertEquals('3', browser.css('#portal-notifications .unread_number').first.text)

    @browsing
    def test_number_of_unread_messages_counts_only_badge_notifications(self, browser):
        self.login(self.dossier_responsible, browser)
        create(Builder('notification').watcher(self.dossier_responsible_watcher).having(activity=self.activity_a))
        create(
            Builder('notification')
            .watcher(self.dossier_responsible_watcher)
            .having(activity=self.activity_b, is_badge=False),
        )
        browser.open()
        self.assertEquals('1', browser.css('#portal-notifications .unread_number').first.text)

    @browsing
    def test_number_of_unread_messages_is_not_display_when_its_0(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open()
        self.assertEquals([], browser.css('#portal-notifications .num-unread'))

    @browsing
    def test_read_url(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open()
        self.assertEquals(
            'http://nohost/plone/notifications/read',
            browser.css('dl.notificationsMenu').first.get('data-read-url'),
        )

    @browsing
    def test_list_url(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open()
        self.assertEquals(
            'http://nohost/plone/notifications/list',
            browser.css('dl.notificationsMenu').first.get('data-list-url'),
        )
