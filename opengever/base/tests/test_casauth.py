from opengever.base.casauth import get_cas_server_url
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile


class TestCASServerURL(FunctionalTestCase):

    def test_cas_plugin_server_url_is_based_on_public_url(self):
        get_current_admin_unit().public_url = 'http://example.com/foobar'
        applyProfile(self.layer['portal'], 'opengever.setup:casauth')
        cas_plugin = self.portal.acl_users.cas_auth
        self.assertEquals(
            'http://example.com/foobar/portal', cas_plugin.cas_server_url)

    def test_cas_server_url_is_fetched_from_plugin(self):
        applyProfile(self.layer['portal'], 'opengever.setup:casauth')
        cas_plugin = self.portal.acl_users.cas_auth
        cas_plugin.cas_server_url = 'http://cas.example.org'
        self.assertEquals('http://cas.example.org', get_cas_server_url())

    def test_trailing_slashes_are_stripped(self):
        get_current_admin_unit().public_url = 'http://example.com/'
        applyProfile(self.layer['portal'], 'opengever.setup:casauth')
        self.assertEquals('http://example.com/portal', get_cas_server_url())
