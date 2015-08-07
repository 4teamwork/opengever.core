from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.center import NotificationCenter
from opengever.base.oguid import Oguid
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestMyNotifications(FunctionalTestCase):

    def setUp(self):
        super(TestMyNotifications, self).setUp()

        create(Builder('ogds_user').having(userid='peter.mueller',
                                           firstname='Peter',
                                           lastname='Mueller'))
        create(Builder('ogds_user').having(userid='hugo.boss',
                                           firstname='Hugo',
                                           lastname='Boss'))

        self.center = NotificationCenter()
        self.test_user = create(Builder('watcher')
                                .having(user_id=TEST_USER_ID))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.test_user]))
        self.resource_b = create(Builder('resource')
                                 .oguid('fd:456')
                                 .watchers([self.test_user]))

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
            {'en': 'Task bla accepted by Peter'},
            'peter.mueller',
            {'en': None}).get('activity')
        self.activity_3 = self.center.add_activity(
            Oguid('fd', '456'),
            'task-added',
            {'en': 'Kennzahlen 2014 erfassen'},
            {'en': 'Task added'},
            {'en': 'Task foo added by peter'},
            'peter.mueller',
            {'en': None}).get('activity')

    @browsing
    def test_lists_only_notifications_of_current_user(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        links = [link.get('href') for link in browser.css('.listing a')]
        self.assertEquals(
            ['http://nohost/plone/@@resolve_notification?notification_id=1',
             'http://nohost/plone/@@resolve_notification?notification_id=2'],
            links)

    @browsing
    def test_listing_content(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        self.assertEquals(
            [{'Actor': 'Boss Hugo (hugo.boss)',
              'Created': api.portal.get_localized_time(
                  self.activity_1.created, long_format=True),
              'Kind': 'task-added',
              'Title': 'Kennzahlen 2014 erfassen'},
             {'Actor': 'Mueller Peter (peter.mueller)',
              'Created': api.portal.get_localized_time(
                  self.activity_2.created, long_format=True),
              'Kind': 'task-transition-open-in-progress',
              'Title': 'Kennzahlen 2014 erfassen'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_title_is_linked_to_resolve_notification_view(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        row = browser.css('.listing tr')[1]
        link = row.css('a').first

        self.assertEquals('Kennzahlen 2014 erfassen', link.text)
        self.assertEquals(
            'http://nohost/plone/@@resolve_notification?notification_id=1',
            link.get('href'))
