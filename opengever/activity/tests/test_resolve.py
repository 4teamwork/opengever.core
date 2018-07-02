from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.browser import resolve_notification_url
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
import transaction


class TestResolveNotificationView(FunctionalTestCase):

    def test_resolve_notification_url(self):
        notification = create(Builder('notification')
                              .id('123')
                              .having(userid='peter'))
        url = resolve_notification_url(notification)
        self.assertEquals(
            'http://example.com/@@resolve_notification?notification_id=123',
            url)

    @browsing
    def test_raises_notfound_when_notification_id_is_missing(self, browser):
        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(self.portal, view='resolve_notification')

    @browsing
    def test_raises_notfound_when_notification_id_is_invalid(self, browser):
        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(self.portal, view='resolve_notification',
                                 data={'notification_id': '123'})

    @browsing
    def test_raises_unauthorized_when_notification_is_not_for_the_current_user(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid='hugo.boss'))

        with browser.expect_unauthorized():
            browser.login().open(
                self.portal,
                view='resolve_notification?notification_id={}'.format(
                    notification.notification_id))

    @browsing
    def test_mark_notification_as_read(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid=TEST_USER_ID))

        browser.login().open(self.portal, view='resolve_notification',
                             data={'notification_id': notification.notification_id})

        notification = notification_center().get_notification(
            notification.notification_id)

        self.assertTrue(notification.is_read)

    @browsing
    def test_redirects_to_the_object_if_its_on_the_current_admin_unit(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid=TEST_USER_ID))

        browser.login().open(self.portal, view='resolve_notification',
                             data={'notification_id': notification.notification_id})

        self.assertEquals(task.absolute_url(), browser.url)

    @browsing
    def test_raises_notfound_when_oguid_does_no_longer_exists(self, browser):
        task = create(Builder('task'))
        oguid = Oguid.for_object(task)

        resource = create(Builder('resource').oguid(oguid.id))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid=TEST_USER_ID))

        with elevated_privileges():
            # This happens on rejecting a submitte proposal within the
            # opengever.meeting-module. A submtited proposal will be deleted
            # on rejecting and is no longer resolveable.
            api.content.delete(task)
            transaction.commit()

        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(self.portal, view='resolve_notification',
                                 data={'notification_id': notification.notification_id})

    @browsing
    def test_redirects_to_the_resolveoguid_on_admin_unit_for_foreign_ressources(self, browser):

        create(Builder('admin_unit')
               .having(public_url='http://example.com/additional')
               .id('additional'))

        resource = create(Builder('resource').oguid('additional:123'))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid=TEST_USER_ID))

        # Calling the resolve_notification view for a foreign object should
        # raise an NotFound exception,  because the view redirects to the
        # foreign admin_unit. But we can't setup a second plone site
        # in this test.
        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(
                self.portal, view='resolve_notification',
                data={'notification_id': notification.notification_id})
