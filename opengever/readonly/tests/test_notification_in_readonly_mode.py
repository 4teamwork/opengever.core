from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Notification
from opengever.activity.model import Resource
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
import json


class TestNotificationRedirectReadOnlyMode(IntegrationTestCase):

    features = ('activity', )

    def setUp(self):
        super(TestNotificationRedirectReadOnlyMode, self).setUp()

        with self.login(self.regular_user):
            resource = Resource.query.get_by_oguid(Oguid.for_object(self.task))
            activity = create(Builder('activity').having(resource=resource))
            self.notification_id = 123
            create(
                Builder('notification')
                .id(self.notification_id)
                .having(activity=activity, userid=self.regular_user.id),
            )
            # Refresh the SQL object
            self.notification = Notification.query.get(self.notification_id)

    @browsing
    def test_redirect_is_not_prevented_by_attempt_to_mark_as_read(self, browser):
        self.login(self.regular_user, browser)

        with ZODBStorageInReadonlyMode():
            browser.open(
                self.portal,
                view='resolve_notification',
                data={'notification_id': self.notification.notification_id})

        self.assertEquals(self.task.absolute_url(), browser.url)
        self.assertFalse(self.notification.is_read)

    @browsing
    def test_following_notification_via_api_is_not_prevented_by_attempt_to_mark_as_read(self, browser):
        self.login(self.regular_user, browser)

        with ZODBStorageInReadonlyMode():
            browser.open(
                self.portal,
                method='PATCH',
                view='@notifications/%s/123' % self.regular_user.id,
                data=json.dumps({'read': True}),
                headers=self.api_headers)

        self.assertEquals(204, browser.status_code)
        self.assertFalse(self.notification.is_read)
