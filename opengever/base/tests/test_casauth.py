from ftw.builder import Builder
from ftw.builder import create
from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import get_cluster_base_url
from opengever.base.casauth import get_gever_portal_url
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone.app.testing import applyProfile


class TestClusterBaseURL(IntegrationTestCase):

    def test_is_equal_to_public_url_for_single_admin_unit_setup(self):
        admin_unit = get_current_admin_unit()
        # For setups with a single admin units, the admin unit's ID is
        # usually omitted from the public_url
        admin_unit.public_url = 'http://lab.example.com'

        # In this case, the cluster base URL is equivalent to public_url
        self.assertEquals(
            'http://lab.example.com/', get_cluster_base_url())

    def test_is_different_from_public_url_for_multi_admin_unit_setup(self):
        create(Builder('admin_unit')
               .having(title=u'Ratzskanzlei',
                       unit_id=u'rk',
                       public_url='http://dev.example.com/rk'))

        admin_unit = get_current_admin_unit()
        # For setups with multiple admin units, an admin unit's public_url
        # ends with the admin unit ID
        admin_unit.public_url = 'http://dev.example.com/{}'.format(
            admin_unit.unit_id)

        # Cluster base URL should NOT end with the admin unit ID.
        self.assertEquals(
            'http://dev.example.com/', get_cluster_base_url())


class TestCASServerURL(IntegrationTestCase):

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

    def test_cas_server_url_is_none_if_cas_plugin_is_missing(self):
        self.assertEquals(None, get_cas_server_url())


class TestGEVERPortalURL(IntegrationTestCase):

    def test_gever_portal_url_is_based_on_cluster_url(self):
        # Cluster base URL is equal to admin unit's public_url *for now*
        get_current_admin_unit().public_url = 'http://example.com/foobar'
        self.assertEquals(
            'http://example.com/foobar/portal', get_gever_portal_url())
