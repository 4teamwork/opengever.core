from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.center import NotificationCenter
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING_SQLITE
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
import transaction


class TestMyNotifications(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING_SQLITE

    def setUp(self):
        super(TestMyNotifications, self).setUp()

        create(Builder('ogds_user').having(userid=u'peter.mueller',
                                           firstname=u'Peter',
                                           lastname=u'M\xfcller'))
        create(Builder('ogds_user').having(userid=u'hugo.boss',
                                           firstname=u'Hugo',
                                           lastname=u'B\xf6ss'))

        self.center = NotificationCenter()
        self.test_user = create(Builder('watcher')
                                .having(actorid=TEST_USER_ID))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.test_user]))
        self.resource_b = create(Builder('resource')
                                 .oguid('fd:456')
                                 .watchers([self.test_user]))

        self.activity_1 = self.center.add_activity(
            Oguid('fd', '123'),
            u'task-added',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe hinzugef\xfcgt'},
            {'de': u'Neue Aufgabe hinzugef\xfcgt durch Hugo B\xf6ss'},
            'hugo.boss',
            {'de': None}).get('activity')
        self.activity_2 = self.center.add_activity(
            Oguid('fd', '123'),
            u'task-transition-open-in-progress',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe akzeptiert'},
            {'de': u'Aufgabe akzeptiert durch Hugo B\xf6ss'},
            'peter.mueller',
            {'de': None}).get('activity')
        self.activity_3 = self.center.add_activity(
            Oguid('fd', '456'),
            u'task-added',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe hinzugef\xfcgt'},
            {'de': u'Neue Aufgabe hinzugef\xfcgt durch Peter M\xfcller'},
            'peter.mueller',
            {'de': None}).get('activity')
        transaction.commit()

    @browsing
    def test_lists_only_notifications_of_current_user(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        links = [link.get('href') for link in browser.css('.listing a')]
        self.assertEquals(
            ['http://example.com/@@resolve_notification?notification_id=1',
             'http://example.com/@@resolve_notification?notification_id=2',
             'http://example.com/@@resolve_notification?notification_id=3'],
            links)

    @browsing
    def test_listing_content(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        self.maxDiff = None
        self.assertEquals(
            [{'Actor': u'B\xf6ss Hugo (hugo.boss)',
              'Created': api.portal.get_localized_time(
                  self.activity_1.created, long_format=True),
              'Kind': u'Aufgabe hinzugef\xfcgt',
              'Title': u'Kennzahlen 2014 \xfcbertragen'},
             {'Actor': u'M\xfcller Peter (peter.mueller)',
              'Created': api.portal.get_localized_time(
                  self.activity_2.created, long_format=True),
              'Kind': u'Aufgabe akzeptiert',
              'Title': u'Kennzahlen 2014 \xfcbertragen'},
             {'Actor': u'M\xfcller Peter (peter.mueller)',
              'Created': api.portal.get_localized_time(
                  self.activity_3.created, long_format=True),
              'Kind': u'Aufgabe hinzugef\xfcgt',
              'Title': u'Kennzahlen 2014 \xfcbertragen'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_title_is_linked_to_resolve_notification_view(self, browser):
        browser.login().open(self.portal,
                             view='tabbedview_view-mynotifications')

        row = browser.css('.listing tr')[1]
        link = row.css('a').first

        self.assertEquals(u'Kennzahlen 2014 \xfcbertragen', link.text)
        self.assertEquals(
            'http://example.com/@@resolve_notification?notification_id=1',
            link.get('href'))
