from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.browser.resolve import ResolveNotificationView
from opengever.base.oguid import Oguid
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zExceptions import NotFound
from zExceptions import Unauthorized


class TestResolveNotificationView(FunctionalTestCase):

    def test_url_for(self):
        url = ResolveNotificationView.url_for('123')
        self.assertEquals(
            'http://example.com/@@resolve_notification?notification_id=123',
            url)

    @browsing
    def test_raises_notfound_when_notification_id_is_missing(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.portal, view='resolve_notification')

    @browsing
    def test_raises_notfound_when_notification_id_is_invalid(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.portal, view='resolve_notification',
                                 data={'notification_id': '123'})

    @browsing
    def test_raises_unauthorized_when_notification_watcher_is_not_the_current_user(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        watcher = create(Builder('watcher').having(user_id='hugo.boss'))
        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, watcher=watcher))

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.portal, view='resolve_notification',
                data={'notification_id': notification.notification_id})

    @browsing
    def test_mark_notification_as_read(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        watcher = create(Builder('watcher').having(user_id=TEST_USER_ID))
        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, watcher=watcher))

        browser.login().open(self.portal, view='resolve_notification',
                             data={'notification_id': notification.notification_id})

        notification = notification_center().get_notification(
            notification.notification_id)

        self.assertTrue(notification.read)

    @browsing
    def test_redirects_to_the_object_if_its_on_the_current_admin_unit(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        watcher = create(Builder('watcher').having(user_id=TEST_USER_ID))
        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, watcher=watcher))

        browser.login().open(self.portal, view='resolve_notification',
                             data={'notification_id': notification.notification_id})

        self.assertEquals(task.absolute_url(), browser.url)

    @browsing
    def test_redirects_to_the_resolveoguid_on_admin_unit_for_foreign_ressources(self, browser):

        create(Builder('admin_unit')
               .having(public_url='http://example.com/additional')
               .id('additional'))

        watcher = create(Builder('watcher').having(user_id=TEST_USER_ID))
        resource = create(Builder('resource').oguid('additional:123'))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, watcher=watcher))

        # Calling the resolve_notification view for a foreign object should
        # raise an NotFound exception,  because the view redirects to the
        # foreign admin_unit. But we can't setup a second plone site
        # in this test.
        with self.assertRaises(NotFound):
            browser.login().open(
                self.portal, view='resolve_notification',
                data={'notification_id': notification.notification_id})
