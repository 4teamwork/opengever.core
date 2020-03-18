from ftw.testbrowser import browsing
from opengever.setup.casauth import install_cas_auth_plugin
from opengever.testing import IntegrationTestCase
from plone import api


class TestLogoutWithoutCASAuth(IntegrationTestCase):

    @browsing
    def test_url_is_plone_logout(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='logout_url')
        self.assertEquals('http://nohost/plone/logout', browser.contents)


class TestLogoutWithCASAuth(IntegrationTestCase):

    def setUp(self):
        super(TestLogoutWithCASAuth, self).setUp()
        install_cas_auth_plugin('portal')

    def tearDown(self):
        super(TestLogoutWithCASAuth, self).tearDown()
        acl_users = api.portal.get_tool('acl_users')
        acl_users.plugins.removePluginById('cas_auth')

    @browsing
    def test_url_is_cas_server_logout(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='logout_url')
        self.assertEquals('http://nohost/portal/logout', browser.contents)
