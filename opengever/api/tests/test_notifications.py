from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity import notification_center
from opengever.activity.model import Notification
from opengever.task.activities import TaskAddedActivity
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestNotificationsGet(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_list_all_notifications_for_the_given_userid(self, browser):
        self.login(self.administrator, browser=browser)

        center = notification_center()

        self.assertEqual(0,  Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        for notification in Notification.query.all():
            notification.is_read = True

        with freeze(datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        self.assertEqual(2, len(center.get_watchers(self.task)))

        # two notifications for each watcher, the responsible and the issuer
        self.assertEqual(4,  Notification.query.count())

        self.login(self.regular_user, browser=browser)

        url = '{}/@notifications/{}'.format(self.portal.absolute_url(),
                                            self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(
            [{u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/3',
              u'actor_id': u'nicole.kohler',
              u'actor_label': u'Kohler Nicole',
              u'created': u'2018-10-16T00:00:00+00:00',
              u'label': u'Task opened',
              u'link': u'http://nohost/plone/@@resolve_notification?notification_id=3',
              u'notification_id': 3,
              u'read': False,
              u'summary': u'New task opened by Ziegler Robert',
              u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'},
             {u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/1',
              u'actor_id': u'nicole.kohler',
              u'actor_label': u'Kohler Nicole',
              u'created': u'2017-10-16T00:00:00+00:00',
              u'label': u'Task opened',
              u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
              u'notification_id': 1,
              u'read': True,
              u'summary': u'New task opened by Ziegler Robert',
              u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'}],
            browser.json.get('items'))

    @browsing
    def test_batch_notifications(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual(0,  Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            for i in range(5):
                TaskAddedActivity(self.task, self.request).record()

        self.login(self.regular_user, browser=browser)

        batch_size = 2
        url = '{}/@notifications/{}?b_size={}'.format(
            self.portal.absolute_url(),
            self.regular_user.getId(),
            batch_size)

        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(5, browser.json.get('items_total'))
        self.assertEquals(2, len(browser.json.get('items')))

        url = browser.json.get('batching').get('last')
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        # 5 notifications with a batchsize of 2 will display only 1 notification
        # on the last batch
        self.assertEquals(1, len(browser.json.get('items')))

    @browsing
    def test_returns_serialized_notifications_for_the_given_userid_and_notification_id(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        self.assertEqual(0,  Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        url = '{}/@notifications/{}/1'.format(self.portal.absolute_url(),
                                              self.regular_user.getId())

        self.login(self.regular_user, browser=browser)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(
            {u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/1',
             u'actor_id': u'robert.ziegler',
             u'actor_label': u'Ziegler Robert',
             u'created': u'2017-10-16T00:00:00+00:00',
             u'label': u'Task opened',
             u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
             u'notification_id': 1,
             u'read': False,
             u'summary': u'New task opened by Ziegler Robert',
             u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'},
            browser.json)

    @browsing
    def test_returned_notifications_are_translated(self, browser):
        self.enable_languages()

        self.login(self.dossier_responsible, browser=browser)
        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        url = '{}/@notifications/{}/1'.format(self.portal.absolute_url(),
                                              self.regular_user.getId())

        self.login(self.regular_user, browser=browser)
        browser.open(url, method='GET', headers={'Accept': 'application/json',
                                                 'Accept-Language': 'fr-ch'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(
            {u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/1',
             u'actor_id': u'robert.ziegler',
             u'actor_label': u'Ziegler Robert',
             u'created': u'2017-10-16T00:00:00+00:00',
             u'label': u'T\xe2che ouverte',
             u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
             u'notification_id': 1,
             u'read': False,
             u'summary': u'Nouvelle t\xe2che ouverte par Ziegler Robert',
             u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'},
            browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = '{}/@notifications'.format(self.portal.absolute_url())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {"message": "Must supply user ID as URL and optional the "
             "notification id as path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_not_found_when_accessing_not_exisiting_notification(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@notifications/{}/1'.format(self.portal.absolute_url(),
                                              self.dossier_responsible.getId())

        with browser.expect_http_error(404):
            browser.open(url, method='GET', headers={'Accept': 'application/json'})

    @browsing
    def test_raises_unauthorized_when_accessing_notification_of_other_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        # Different username in path
        with browser.expect_http_error(401):
            url = '{}/@notifications/{}/1'.format(
                self.portal.absolute_url(), self.regular_user.getId())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        # Own username but foreign notification-id
        with browser.expect_http_error(401):
            url = '{}/@notifications/{}/1'.format(
                self.portal.absolute_url(), self.dossier_responsible.getId())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})


class TestNotificationsPatch(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_mark_notification_as_read(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        TaskAddedActivity(self.task, self.request).record()

        url = '{}/@notifications/{}/{}'.format(self.portal.absolute_url(),
                                               self.regular_user.getId(), 1)

        self.login(self.regular_user, browser=browser)

        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertFalse(Notification.query.first().is_read)

        data = json.dumps({'read': True})
        browser.open(url, data=data, method='PATCH',
                     headers={'Accept': 'application/json'})

        self.assertEqual(204, browser.status_code)
        self.assertTrue(Notification.query.first().is_read)

    @browsing
    def test_raises_not_found_when_accessing_not_exisiting_notification(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@notifications/{}/1'.format(self.portal.absolute_url(),
                                              self.dossier_responsible.getId())

        self.assertEqual(0,  Notification.query.count())

        with browser.expect_http_error(404):
            browser.open(url, method='PATCH', data=json.dumps({}),
                         headers={'Accept': 'application/json'})

    @browsing
    def test_raises_unauthorized_when_accessing_notification_of_other_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        # Different username in path
        with browser.expect_http_error(401):
            url = '{}/@notifications/{}/1'.format(
                self.portal.absolute_url(), self.regular_user.getId())
            browser.open(url, data=json.dumps({}), method='PATCH',
                         headers={'Accept': 'application/json'})

        # Own username but foreign notification-id
        with browser.expect_http_error(401):
            url = '{}/@notifications/{}/1'.format(
                self.portal.absolute_url(), self.dossier_responsible.getId())
            browser.open(url, data=json.dumps({}), method='PATCH',
                         headers={'Accept': 'application/json'})
