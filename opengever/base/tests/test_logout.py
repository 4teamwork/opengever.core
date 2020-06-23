from ftw.testbrowser import browsing
from opengever.setup.casauth import install_cas_auth_plugin
from opengever.testing import IntegrationTestCase
from plone import api


class TestLogoutWithoutCASAuth(IntegrationTestCase):

    @browsing
    def test_redirects_to_plone_logged_out_page(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='@@logout')
        self.assertEquals('http://nohost/plone/logged_out', browser.url)

    @browsing
    def test_deletes_ac_cookie(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.allow_redirects = False
        browser.open(view='@@logout')
        response = browser.get_driver().response

        self.assertEqual(
            {'__ac': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'}},
            response.cookies)


class TestLogoutWithCASAuth(IntegrationTestCase):

    def setUp(self):
        super(TestLogoutWithCASAuth, self).setUp()
        install_cas_auth_plugin('portal')

    def tearDown(self):
        super(TestLogoutWithCASAuth, self).tearDown()
        acl_users = api.portal.get_tool('acl_users')
        acl_users.plugins.removePluginById('cas_auth')

    @browsing
    def test_deletes_ac_cookie(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.allow_redirects = False
        browser.open(view='@@logout')
        response = browser.get_driver().response

        self.assertEqual(
            {'__ac': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'}},
            response.cookies)

    @browsing
    def test_redirects_to_cas_logout(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.raise_http_errors = False
        browser.open(view='@@logout')

        cas_server_url = 'http://nohost/portal'
        self.assertEquals('/'.join((cas_server_url, 'logout')), browser.url)
