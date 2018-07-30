from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.browser import resolve_notification_url
from opengever.activity.model import Notification
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from plone import api


class TestResolveNotificationView(IntegrationTestCase):

    def setUp(self):
        super(TestResolveNotificationView, self).setUp()
        # XXX - Cannot fixturise SQL objects yet.
        with self.login(self.regular_user):
            oguid = Oguid.for_object(self.task)
            resource = create(Builder('resource').oguid(oguid.id))
            activity = create(Builder('activity').having(resource=resource))
            self.notification_id = 123
            create(
                Builder('notification')
                .id(self.notification_id)
                .having(activity=activity, userid=self.regular_user.id),
            )
            # XXX - Refresh the SQL object
            self.notification = Notification.query.get(self.notification_id)

    def test_resolve_notification_url(self):
        self.assertEquals(
            'http://nohost/plone/@@resolve_notification?notification_id=123',
            resolve_notification_url(self.notification),
        )

    @browsing
    def test_raises_notfound_when_notification_id_is_missing(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(reason='Not Found'):
            browser.open(self.portal, view='resolve_notification')

    @browsing
    def test_raises_notfound_when_notification_id_is_invalid(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(reason='Not Found'):
            browser.open(self.portal, view='resolve_notification', data={'notification_id': '1234'})

    @browsing
    def test_raises_notfound_when_oguid_does_no_longer_exists(self, browser):
        # This happens on rejecting a submitte proposal within the
        # opengever.meeting-module. A submtited proposal will be deleted
        # on rejecting and is no longer resolveable.
        self.login(self.manager)
        api.content.delete(self.task)
        with browser.expect_http_error(reason='Not Found'):
            self.login(self.regular_user, browser)
            data = {'notification_id': self.notification.notification_id}
            browser.open(self.portal, view='resolve_notification', data=data)

    @browsing
    def test_redirects_to_the_resolveoguid_on_admin_unit_for_foreign_ressources(self, browser):
        # Calling the resolve_notification view for a foreign object should
        # raise an NotFound exception,  because the view redirects to the
        # foreign admin_unit. But we can't setup a second plone site
        # in this test.
        resource = create(Builder('resource').oguid('additional:{}'.format(self.notification_id)))
        activity = create(Builder('activity').having(resource=resource))
        notification = create(Builder('notification').having(activity=activity, userid=self.regular_user.id))
        with browser.expect_http_error(reason='Not Found'):
            self.login(self.regular_user, browser)
            browser.open(self.portal, view='resolve_notification', data={'notification_id': notification.notification_id})

    @browsing
    def test_mark_notification_as_read(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='resolve_notification', data={'notification_id': self.notification.notification_id})
        self.assertTrue(self.notification.is_read)

    @browsing
    def test_raises_unauthorized_when_notification_is_not_for_the_current_user(self, browser):
        self.login(self.dossier_responsible, browser)
        with browser.expect_unauthorized():
            view = 'resolve_notification?notification_id={}'.format(self.notification.notification_id)
            browser.open(self.portal, view=view)

    @browsing
    def test_redirects_to_the_object_if_its_on_the_current_admin_unit(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='resolve_notification', data={'notification_id': self.notification.notification_id})
        self.assertEquals(self.task.absolute_url(), browser.url)
