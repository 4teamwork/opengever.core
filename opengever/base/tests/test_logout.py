from ftw.testbrowser import browsing
from opengever.setup.casauth import install_cas_auth_plugin
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
import transaction


class TestLogoutWithoutCASAuth(IntegrationTestCase):

    @browsing
    def test_url_is_plone_logout(self, browser):
        browser.login().open(view='logout_url')
        self.assertEquals('http://nohost/plone/logout', browser.contents)


class TestLogoutWithCASAuth(FunctionalTestCase):

    def setUp(self):
        super(TestLogoutWithCASAuth, self).setUp()
        install_cas_auth_plugin()
        transaction.commit()

    def tearDown(self):
        super(TestLogoutWithCASAuth, self).tearDown()
        acl_users = api.portal.get_tool('acl_users')
        acl_users.plugins.removePluginById('cas_auth')
        transaction.commit()

    @browsing
    def test_url_is_cas_server_logout(self, browser):
        browser.login().open(view='logout_url')
        self.assertEquals('http://example.com/portal/logout', browser.contents)
