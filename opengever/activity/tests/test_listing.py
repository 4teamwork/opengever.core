from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.badge import BadgeIconDispatcher
from opengever.activity.center import NotificationCenter
from opengever.activity.model import Watcher
from opengever.activity.model.notification import Notification
from opengever.activity.model.settings import NotificationDefault
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.oguid import Oguid
from opengever.ogds.base.actor import SYSTEM_ACTOR_ID
from opengever.testing import IntegrationTestCase
from plone import api


class TestMyNotifications(IntegrationTestCase):

    def setUp(self):
        super(TestMyNotifications, self).setUp()

        setting = NotificationDefault.query.filter_by(kind='task-added-or-reassigned').one()
        setting.badge_notification_roles = [WATCHER_ROLE, ]
        setting = NotificationDefault.query.filter_by(kind='task-reminder').one()
        setting.badge_notification_roles = [WATCHER_ROLE, ]

        self.center = NotificationCenter(dispatchers=[BadgeIconDispatcher()])

        self.test_watcher = Watcher.query.get_by_actorid(self.regular_user.getId())

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.test_watcher]))
        self.resource_b = create(Builder('resource')
                                 .oguid('fd:456')
                                 .watchers([self.test_watcher]))

        self.activity_1 = self.center.add_activity(
            Oguid('fd', '123'),
            u'task-added',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe hinzugef\xfcgt'},
            {'de': u'Neue Aufgabe hinzugef\xfcgt durch  B\xf6ss'},
            self.dossier_responsible.getId(),
            {'de': None}).get('activity')
        self.activity_2 = self.center.add_activity(
            Oguid('fd', '123'), u'task-reminder',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe akzeptiert'},
            {'de': u'Aufgabe akzeptiert durch Hugo B\xf6ss'},
            self.secretariat_user.getId(),
            {'de': None}).get('activity')
        self.activity_3 = self.center.add_activity(
            Oguid('fd', '456'),
            u'task-added',
            {'de': u'Kennzahlen 2014 \xfcbertragen'},
            {'de': u'Aufgabe hinzugef\xfcgt'},
            {'de': u'Neue Aufgabe hinzugef\xfcgt durch Peter M\xfcller'},
            self.dossier_responsible.getId(),
            {'de': None}).get('activity')

    @browsing
    def test_lists_only_notifications_of_current_user(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mynotifications')

        links = [link.get('href') for link in browser.css('.listing a')]
        self.assertEquals(
            ['http://nohost/plone/@@resolve_notification?notification_id=1',
             'http://nohost/plone/@@resolve_notification?notification_id=2',
             'http://nohost/plone/@@resolve_notification?notification_id=3'],
            links)

    @browsing
    def test_listing_content(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mynotifications')

        self.maxDiff = None
        self.assertEquals(
            [{'Actor': u'Ziegler Robert (robert.ziegler)',
              'Created': api.portal.get_localized_time(
                  self.activity_1.created, long_format=True),
              'Kind': u'Aufgabe hinzugef\xfcgt',
              'Title': u'Kennzahlen 2014 \xfcbertragen'},
             {'Actor': u'K\xf6nig J\xfcrgen (jurgen.konig)',
              'Created': api.portal.get_localized_time(
                  self.activity_2.created, long_format=True),
              'Kind': u'Aufgabe akzeptiert',
              'Title': u'Kennzahlen 2014 \xfcbertragen'},
             {'Actor': u'Ziegler Robert (robert.ziegler)',
              'Created': api.portal.get_localized_time(
                  self.activity_3.created, long_format=True),
              'Kind': u'Aufgabe hinzugef\xfcgt',
              'Title': u'Kennzahlen 2014 \xfcbertragen'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_title_is_linked_to_resolve_notification_view(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mynotifications')

        row = browser.css('.listing tr')[1]
        link = row.css('a').first

        self.assertEquals(u'Kennzahlen 2014 \xfcbertragen', link.text)
        self.assertEquals(
            'http://nohost/plone/@@resolve_notification?notification_id=1',
            link.get('href'))

    @browsing
    def test_my_notification_lists_only_badge_notifications(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mynotifications')

        self.assertEquals(4, len(browser.css('.listing').first.rows))

        notifications = Notification.query.filter_by(userid=self.regular_user.getId())
        notifications[0].is_badge = False

        browser.open(self.portal, view='tabbedview_view-mynotifications')
        self.assertEquals(3, len(browser.css('.listing').first.rows))

    @browsing
    def test_hide_system_actor_id(self, browser):
        self.login(self.regular_user, browser=browser)

        self.activity_2.actor_id = SYSTEM_ACTOR_ID

        browser.open(self.portal, view='tabbedview_view-mynotifications')
        self.assertEquals(
            [u'Ziegler Robert (robert.ziegler)',
             u'',
             u'Ziegler Robert (robert.ziegler)'],
            [row.get('Actor') for row in browser.css('.listing').first.dicts()])
