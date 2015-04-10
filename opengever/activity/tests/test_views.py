from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.center import NotificationCenter
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestNotificationView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestNotificationView, self).setUp()

        self.center = NotificationCenter()
        self.test_user = create(Builder('watcher')
                                .having(user_id=TEST_USER_ID))

        self.resource_a = create(Builder('resource')
                                 .oguid('fd:123')
                                 .watchers([self.test_user]))

        self.activity_1 = self.center.add_activity(
            Oguid('fd', '123'), 'task-added', 'Kennzahlen 2014 erfassen',
            'Task bla added', 'hugo.boss')

        self.activity_2 = self.center.add_activity(
            Oguid('fd', '123'), 'task-transition-open-in-progress',
            'Kennzahlen 2014 erfassen', 'Task bla added', 'hugo.boss')

        self.notifications = self.center.get_users_notifications(TEST_USER_ID)

    @browsing
    def test_mark_notification_as_read(self, browser):
        notification_id = self.notifications[0].notification_id
        browser.login().open(self.portal, view='notifications/read',
                             data={'notification_id': notification_id})

        notifications = self.center.get_users_notifications(TEST_USER_ID)
        self.assertTrue(notifications[0].read)
        self.assertFalse(notifications[1].read)

    @browsing
    def test_mark_invalid_notification_as_read_raise_attribute_error(self, browser):
        with self.assertRaises(AttributeError):
            browser.login().open(self.portal, view='notifications/read',
                                 data={'notification_id': '234'})
