from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin


class TestCASAuthSetup(FunctionalTestCase):

    def test_ldap_plugin_is_disabled(self):
        applyProfile(
            self.layer['portal'], 'opengever.examplecontent:4teamwork-ldap')
        applyProfile(
            self.layer['portal'], 'opengever.setup:casauth')
        self.assertNotIn(
            'ldap',
            self.portal.acl_users.plugins.listPluginIds(IAuthenticationPlugin))
