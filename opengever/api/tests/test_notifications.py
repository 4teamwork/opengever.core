from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity import notification_center
from opengever.activity.model import Notification
from opengever.base.oguid import Oguid
from opengever.task.activities import TaskAddedActivity
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestNotificationsGet(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_returns_notifications_for_the_given_userid(self, browser):
        self.login(self.administrator, browser=browser)

        center = notification_center()

        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        for notification in Notification.query.all():
            notification.is_read = True

        with freeze(datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        self.assertEqual(2, len(center.get_watchers(self.task)))

        # two notifications for each watcher, the responsible and the issuer
        self.assertEqual(4, Notification.query.count())

        self.login(self.regular_user, browser=browser)

        url = '{}/@notifications/{}'.format(self.portal.absolute_url(),
                                            self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(
            [{u'@id': u'http://nohost/plone/@notifications/%s/4' % self.regular_user.id,
              u'actor_id': self.administrator.id,
              u'actor_label': u'Kohler Nicole',
              u'created': u'2018-10-16T00:00:00+00:00',
              u'label': u'Task opened',
              u'link': u'http://nohost/plone/@@resolve_notification?notification_id=4',
              u'notification_id': 4,
              u'oguid': str(Oguid.for_object(self.task)),
              u'read': False,
              u'summary': u'New task opened by Ziegler Robert',
              u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'},
             {u'@id': u'http://nohost/plone/@notifications/%s/2' % self.regular_user.id,
              u'actor_id': self.administrator.id,
              u'actor_label': u'Kohler Nicole',
              u'created': u'2017-10-16T00:00:00+00:00',
              u'label': u'Task opened',
              u'link': u'http://nohost/plone/@@resolve_notification?notification_id=2',
              u'notification_id': 2,
              u'oguid': str(Oguid.for_object(self.task)),
              u'read': True,
              u'summary': u'New task opened by Ziegler Robert',
              u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'}],
            browser.json.get('items'))

    @browsing
    def test_list_only_badge_notifications(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()

        self.login(self.regular_user, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(),
                                            self.regular_user.getId())

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(3, browser.json['items_total'])
        notification_id = browser.json['items'][1]['notification_id']
        Notification.query.filter(Notification.notification_id ==
                                  notification_id).one().is_badge = False
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(2, browser.json['items_total'])

    @browsing
    def test_batch_notifications(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            for i in range(5):
                TaskAddedActivity(self.task, self.request).record()

        self.login(self.regular_user, browser=browser)

        batch_size = 2
        base_url = '{}/@notifications/{}'.format(
            self.portal.absolute_url(),
            self.regular_user.getId())
        url = '{}?b_size={}'.format(base_url, batch_size)

        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(5, browser.json.get('items_total'))
        self.assertEquals(2, len(browser.json.get('items')))
        self.assertDictEqual(
            {"@id": url,
             "first": '{}?b_start=0&b_size={}'.format(base_url, batch_size),
             "last": '{}?b_start=4&b_size={}'.format(base_url, batch_size),
             "next": '{}?b_start=2&b_size={}'.format(base_url, batch_size)},
            browser.json.get('batching')
        )

        url = browser.json.get('batching').get('last')
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        # 5 notifications with a batchsize of 2 will display only 1 notification
        # on the last batch
        self.assertEquals(1, len(browser.json.get('items')))

    @browsing
    def test_returns_serialized_notifications_for_the_given_userid_and_notification_id(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request).record()

        url = '{}/@notifications/{}/1'.format(self.portal.absolute_url(),
                                              self.regular_user.getId())

        self.login(self.regular_user, browser=browser)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)

        self.assertEquals(
            {u'@id': u'http://nohost/plone/@notifications/%s/1' % self.regular_user.id,
             u'actor_id': self.dossier_responsible.id,
             u'actor_label': u'Ziegler Robert',
             u'created': u'2017-10-16T00:00:00+00:00',
             u'label': u'Task opened',
             u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
             u'notification_id': 1,
             u'oguid': str(Oguid.for_object(self.task)),
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
            {u'@id': u'http://nohost/plone/@notifications/%s/1' % self.regular_user.id,
             u'actor_id': self.dossier_responsible.id,
             u'actor_label': u'Ziegler Robert',
             u'created': u'2017-10-16T00:00:00+00:00',
             u'label': u'T\xe2che ouverte',
             u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
             u'notification_id': 1,
             u'oguid': str(Oguid.for_object(self.task)),
             u'read': False,
             u'summary': u'Nouvelle t\xe2che ouverte par Ziegler Robert',
             u'title': u'Vertr\xe4ge mit der kantonalen... - Vertragsentwurf \xdcberpr\xfcfen'},
            browser.json)

    @browsing
    def test_returned_notifications_are_sorted_unread_first(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()

        self.login(self.regular_user, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(),
                                            self.regular_user.getId())

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(3, browser.json['items_total'])
        notification_ids = [el['notification_id'] for el in browser.json['items']]

        Notification.query.filter(Notification.notification_id ==
                                  notification_ids[0]).one().is_read = True
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(3, browser.json['items_total'])
        notification_ids.append(notification_ids.pop(0))
        self.assertEqual(
            notification_ids,
            [el['notification_id'] for el in browser.json['items']])

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

        self.assertEqual(0, Notification.query.count())

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


class TestNotificationsPost(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_mark_notifications_as_read(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()
        TaskAddedActivity(self.task, self.request).record()

        url = '{}/@notifications/{}'.format(self.portal.absolute_url(), self.regular_user.getId())
        self.login(self.regular_user, browser=browser)
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual([False, False, False],
                         [notification.is_read for notification in Notification.query.all()])

        browser.open(url, method='POST', headers=self.api_headers,
                     data=json.dumps({'mark_all_notifications_as_read': True,
                                      'latest_client_side_notification': 2}))

        self.assertEqual(204, browser.status_code)

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([True, True, False],
                         [notification.is_read for notification in Notification.query.all()])

    @browsing
    def test_raises_unauthorized_when_accessing_notifications_of_other_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(), self.regular_user.getId())
        with browser.expect_http_error(401):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=json.dumps({'mark_all_notifications_as_read': True,
                                          'latest_client_side_notification': 0}))
        self.assertEqual({"message": "It's not allowed to access notifications of other users.",
                          "type": "Unauthorized"}, browser.json)

    @browsing
    def test_post_notifications_without_user_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@notifications',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'mark_all_notifications_as_read': True,
                                          'latest_client_side_notification': 0}))
        self.assertEqual(
            {"message": "Must supply user ID as path parameter.",
             "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_notifications_without_mark_all_notifications_as_read_raises_bad_request(self,
                                                                                          browser):
        self.login(self.regular_user, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(), self.regular_user.getId())
        with browser.expect_http_error(400):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'latest_client_side_notification': 0}))
        self.assertEqual({"message":
                          "Property 'mark_all_notifications_as_read' is required and must be true.",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_notifications_with_non_numerical_notification_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(), self.regular_user.getId())
        with browser.expect_http_error(400):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'mark_all_notifications_as_read': True,
                                          'latest_client_side_notification': 'invalid'}))
        self.assertEqual({
            "message":
            "Property 'latest_client_side_notification' is required and must be an integer.",
            "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_notifications_with_invalid_notification_id_raises_bad_request(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        TaskAddedActivity(self.task, self.request).record()
        self.login(self.regular_user, browser=browser)
        url = '{}/@notifications/{}'.format(self.portal.absolute_url(), self.regular_user.getId())
        with browser.expect_http_error(400):
            browser.open(url,
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'mark_all_notifications_as_read': True,
                                          'latest_client_side_notification': 12}))
        self.assertEqual({"message": "User has no notification with notification_id 12.",
                          "type": "BadRequest"}, browser.json)
