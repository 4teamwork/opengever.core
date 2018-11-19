from datetime import datetime
from ftw.testbrowser import restapi
from ftw.testing import freeze
from opengever.activity import notification_center
from opengever.activity.model import Notification
from opengever.task.activities import TaskAddedActivity
from opengever.testing import IntegrationTestCase
import pytz


class TestNotificationsGet(IntegrationTestCase):

    features = ('activity', )

    @restapi
    def test_list_all_notifications_for_the_given_userid(self, api_client):
        self.login(self.administrator, api_client)
        center = notification_center()
        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        for notification in Notification.query.all():
            notification.is_read = True

        with freeze(datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        self.assertEqual(2, len(center.get_watchers(self.task)))
        # two notifications for each watcher, the responsible and the issuer
        self.assertEqual(4, Notification.query.count())

        self.login(self.regular_user, api_client)
        endpoint = '@notifications/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)
        self.assertEqual(200, api_client.status_code)

        expected_items = [
            {
                u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/3',
                u'created': u'2018-10-16T00:00:00+00:00',
                u'label': u'Task opened',
                u'link': u'http://nohost/plone/@@resolve_notification?notification_id=3',
                u'notification_id': 3,
                u'read': False,
                u'summary': u'New task opened by Ziegler Robert',
                u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
            },
            {
                u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/1',
                u'created': u'2017-10-16T00:00:00+00:00',
                u'label': u'Task opened',
                u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
                u'notification_id': 1,
                u'read': True,
                u'summary': u'New task opened by Ziegler Robert',
                u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
            },
        ]
        self.assertEqual(expected_items, api_client.contents.get('items'))

    @restapi
    def test_batch_notifications(self, api_client):
        self.login(self.administrator, api_client)
        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            for _i in range(5):
                TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        self.login(self.regular_user, api_client)
        batch_size = 2
        endpoint = '@notifications/{}?b_size={}'.format(self.regular_user.getId(), batch_size)
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual(5, api_client.contents.get('items_total'))
        self.assertEqual(2, len(api_client.contents.get('items')))

        url = api_client.contents.get('batching').get('last')
        api_client.open(url)

        # 5 notifications with a batchsize of 2 will display only 1 notification
        # on the last batch
        self.assertEqual(1, len(api_client.contents.get('items')))

    @restapi
    def test_returns_serialized_notifications_for_the_given_userid_and_notification_id(self, api_client):
        self.login(self.dossier_responsible, api_client)
        self.assertEqual(0, Notification.query.count())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        endpoint = '@notifications/{}/1'.format(self.regular_user.getId())

        self.login(self.regular_user, api_client)
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        expected_notification = {
            u'@id': u'http://nohost/plone/@notifications/kathi.barfuss/1',
            u'created': u'2017-10-16T00:00:00+00:00',
            u'label': u'Task opened',
            u'link': u'http://nohost/plone/@@resolve_notification?notification_id=1',
            u'notification_id': 1,
            u'read': False,
            u'summary': u'New task opened by Ziegler Robert',
            u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
        }
        self.assertEqual(expected_notification, api_client.contents)

    @restapi
    def test_raises_bad_request_when_userid_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(400):
            api_client.open(endpoint='@notifications')

        expected_error = {
            "message": "Must supply user ID as URL and optional the notification id as path parameter.",
            "type": "BadRequest",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_not_found_when_accessing_not_exisiting_notification(self, api_client):
        self.login(self.dossier_responsible, api_client)
        endpoint = '@notifications/{}/1'.format(self.dossier_responsible.getId())

        with api_client.expect_http_error(404):
            api_client.open(endpoint=endpoint)

    @restapi
    def test_raises_unauthorized_when_accessing_notification_of_other_user(self, api_client):
        self.login(self.dossier_responsible, api_client)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        # Different username in path
        with api_client.expect_http_error(401):
            endpoint = '@notifications/{}/1'.format(self.regular_user.getId())
            api_client.open(endpoint=endpoint)

        # Own username but foreign notification-id
        with api_client.expect_http_error(401):
            endpoint = '@notifications/{}/1'.format(self.dossier_responsible.getId())
            api_client.open(endpoint=endpoint)


class TestNotificationsPatch(IntegrationTestCase):

    features = ('activity', )

    @restapi
    def test_mark_notification_as_read(self, api_client):
        self.login(self.dossier_responsible, api_client)
        TaskAddedActivity(self.task, self.request, self.task.__parent__).record()
        endpoint = '@notifications/{}/1'.format(self.regular_user.getId())
        self.login(self.regular_user, api_client)
        api_client.open(endpoint=endpoint)

        self.assertFalse(Notification.query.first().is_read)

        data = {'read': True}
        api_client.open(endpoint=endpoint, data=data, method='PATCH')

        self.assertEqual(204, api_client.status_code)
        self.assertTrue(Notification.query.first().is_read)

    @restapi
    def test_raises_not_found_when_accessing_not_exisiting_notification(self, api_client):
        self.login(self.dossier_responsible, api_client)
        self.assertEqual(0, Notification.query.count())

        with api_client.expect_http_error(404):
            endpoint = '@notifications/{}/1'.format(self.dossier_responsible.getId())
            api_client.open(endpoint=endpoint, data={}, method='PATCH')

    @restapi
    def test_raises_unauthorized_when_accessing_notification_of_other_user(self, api_client):
        self.login(self.dossier_responsible, api_client)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            TaskAddedActivity(self.task, self.request, self.task.__parent__).record()

        # Different username in path
        with api_client.expect_http_error(401):
            endpoint = '@notifications/{}/1'.format(self.regular_user.getId())
            api_client.open(endpoint=endpoint, data={}, method='PATCH')

        # Own username but foreign notification-id
        with api_client.expect_http_error(401):
            endpoint = '@notifications/{}/1'.format(self.dossier_responsible.getId())
            api_client.open(endpoint=endpoint, data={}, method='PATCH')
