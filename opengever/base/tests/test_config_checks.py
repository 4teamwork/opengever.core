from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.base.config_checks.checks import BaseCheck
from opengever.base.config_checks.manager import ConfigCheckManager
from opengever.base.interfaces import IConfigCheck
from opengever.bundle.ldap import LDAP_PLUGIN_META_TYPES
from opengever.testing import IntegrationTestCase
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.component import adapter
from zope.component import getSiteManager
from zope.interface import implementer
from zope.interface import Interface


@implementer(IConfigCheck)
@adapter(Interface)
class DummyCheckMissconfigured1(BaseCheck):
    def check(self):
        return self.config_error(title="Dummy check 1", description="Description 1")


@implementer(IConfigCheck)
@adapter(Interface)
class DummyCheckMissconfigured2(BaseCheck):
    def check(self):
        return self.config_error(title="Dummy check 2")


class TestConfigCheckManager(IntegrationTestCase):

    def test_check_all_returns_an_empty_list_if_everything_is_ok(self):
        self.login(self.manager)
        self.assertEqual([], ConfigCheckManager().check_all())

    def test_check_all_returns_an_error_dict_for_each_failing_check(self):
        self.login(self.manager)
        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")
        getSiteManager().registerAdapter(DummyCheckMissconfigured2, name="check-missconfigured-2")

        self.assertItemsEqual([
            {'id': 'DummyCheckMissconfigured1', 'title': 'Dummy check 1', 'description': 'Description 1'},
            {'id': 'DummyCheckMissconfigured2', 'title': 'Dummy check 2', 'description': ''}
        ], ConfigCheckManager().check_all())

    def test_check_for_ldap_plugin_order(self):
        self.login(self.manager)

        self.assertEqual(0, len(ConfigCheckManager().check_all()))

        # Set the meta-type of the last auth plugin to an ldap plugin meta type
        # to simulate a bad plugin order
        plugins = api.portal.get_tool('acl_users').plugins.listPlugins(IAuthenticationPlugin)
        plugins[-1][1].meta_type = LDAP_PLUGIN_META_TYPES[0]

        self.assertEqual(1, len(ConfigCheckManager().check_all()))


class TestConfigCheckViewlet(IntegrationTestCase):

    @browsing
    def test_show_errors_in_a_plone_viewlet_for_managers(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.portal)
        statusmessages.assert_no_messages()

        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")

        browser.reload()

        statusmessages.assert_message('Dummy check 1 Description 1')

    @browsing
    def test_show_error_viewlet_only_for_managers(self, browser):
        self.login(self.manager, browser=browser)

        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")
        browser.open(self.portal)

        self.assertEqual(1, len(statusmessages.messages().get('error')))

        self.login(self.administrator, browser=browser)
        browser.reload()

        statusmessages.assert_no_messages()
