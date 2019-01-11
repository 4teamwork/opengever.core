from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase


class TestResolveOGUIDView(IntegrationTestCase):

    def setUp(self):
        create(Builder('admin_unit')
               .id("remote-admin-unit")
               .having(public_url='http://nohost/remote-au'))
        super(TestResolveOGUIDView, self).setUp()

    @browsing
    def test_check_permissions_fails_with_nobody(self, browser):
        self.login(self.regular_user)
        url = ResolveOGUIDView.url_for(
            Oguid.for_object(self.task), get_current_admin_unit())

        with browser.expect_unauthorized():
            browser.open(url)

    @browsing
    def test_redirect_if_correct_client(self, browser):
        self.login(self.regular_user, browser=browser)

        url = ResolveOGUIDView.url_for(
            Oguid.for_object(self.task), get_current_admin_unit())

        browser.open(url)
        self.assertEqual(self.task.absolute_url(), browser.url)

    @browsing
    def test_with_get_parameter_ids(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.task)
        url = "{}/@@resolve_oguid?oguid={}".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(self.task.absolute_url(), browser.url)

    @browsing
    def test_with_traversal_based_ids(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid/{}".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(self.document.absolute_url(), browser.url)

    @browsing
    def test_to_specific_view(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid/{}/tooltip".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(
            '{}/tooltip'.format(self.document.absolute_url()), browser.url)

    @browsing
    def test_preserves_query_string_in_qs_style_url(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid?oguid={}&foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(
            '{}?foo=bar&key=value'.format(self.document.absolute_url()),
            browser.url)

    @browsing
    def test_preserves_query_string_in_traversal_style_url(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid/{}?foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(
            '{}?foo=bar&key=value'.format(self.document.absolute_url()),
            browser.url)

    @browsing
    def test_preserves_query_string_in_traversal_style_url_with_view(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid/{}/tooltip?foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(
            '{}/tooltip?foo=bar&key=value'.format(self.document.absolute_url()),
            browser.url)

    @browsing
    def test_preserves_query_string_in_remote_qs_style_url(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = 'remote-admin-unit:12345'
        url = "{}/@@resolve_oguid?oguid={}&foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.raise_http_errors = False
        browser.open(url)
        self.assertEqual(
            'http://nohost/remote-au/@@resolve_oguid?oguid=remote-admin-unit:12345?foo=bar&key=value',  # noqa
            browser.url)

    @browsing
    def test_preserves_query_string_in_remote_traversal_style_url(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = 'remote-admin-unit:12345'
        url = "{}/@@resolve_oguid/{}?foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.raise_http_errors = False
        browser.open(url)
        self.assertEqual(
            'http://nohost/remote-au/@@resolve_oguid?oguid=remote-admin-unit:12345?foo=bar&key=value',  # noqa
            browser.url)

    @browsing
    def test_preserves_query_string_in_remote_traversal_style_url_with_view(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = 'remote-admin-unit:12345'
        url = "{}/@@resolve_oguid/{}/tooltip?foo=bar&key=value".format(
            self.portal.absolute_url(), oguid)

        browser.raise_http_errors = False
        browser.open(url)
        self.assertEqual(
            'http://nohost/remote-au/@@resolve_oguid/remote-admin-unit:12345/tooltip?foo=bar&key=value',  # noqa
            browser.url)

    @browsing
    def test_preserves_query_string_with_multivalued_params(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = "{}/@@resolve_oguid?oguid={}&foo=value1&foo=value2".format(
            self.portal.absolute_url(), oguid)

        browser.open(url)
        self.assertEqual(
            '{}?foo=value1&foo=value2'.format(self.document.absolute_url()),
            browser.url)
