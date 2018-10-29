from ftw.casauth.plugin import CASAuthenticationPlugin
from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution


class TestConfig(IntegrationTestCase):

    @restapi
    def test_config_contains_id(self, api_client):
        self.login(self.regular_user, api_client)
        url = '/'.join((self.portal.absolute_url(), '@config'))
        api_client.open(url)
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(api_client.contents.get(u'@id'), url)

    @restapi
    def test_config_contains_version(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(api_client.contents.get(u'version'), get_distribution('opengever.core').version)

    @restapi
    def test_config_contains_features(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        expected_features = {
            u'activity': False,
            u'archival_file_conversion': False,
            u'contacts': False,
            u'doc_properties': False,
            u'dossier_templates': False,
            u'ech0147_export': False,
            u'ech0147_import': False,
            u'favorites': True,
            u'gever_ui_enabled': False,
            u'gever_ui_path': u'http://localhost:8081/#/',
            u'journal_pdf': False,
            u'meetings': False,
            u'officeatwork': False,
            u'officeconnector_attach': True,
            u'officeconnector_checkout': True,
            u'oneoffixx': False,
            u'preview': False,
            u'preview_auto_refresh': False,
            u'preview_open_pdf_in_new_window': False,
            u'private_tasks': True,
            u'purge_trash': False,
            u'repositoryfolder_documents_tab': True,
            u'repositoryfolder_proposals_tab': True,
            u'repositoryfolder_tasks_tab': True,
            u'resolver_name': u'strict',
            u'sablon_date_format': u'%d.%m.%Y',
            u'solr': False,
            u'tasks_pdf': False,
            u'workspace': False,
        }
        self.assertEqual(expected_features, api_client.contents.get(u'features'))

    @restapi
    def test_config_contains_max_subdossier_depth(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(2, api_client.contents.get(u'max_dossier_levels'))

    @restapi
    def test_config_contains_max_repository_depth(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(api_client.contents.get(u'max_repositoryfolder_levels'), 3)

    @restapi
    def test_config_contains_recently_touched_limit(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(api_client.contents.get(u'recently_touched_limit'), 10)

    @restapi
    def test_config_contains_cas_url(self, api_client):
        # Install CAS plugin
        uf = self.portal.acl_users
        plugin = CASAuthenticationPlugin('cas_auth', cas_server_url='https://cas.server.local')
        uf._setObject(plugin.getId(), plugin)
        plugin = uf['cas_auth']
        plugin.manage_activateInterfaces([
            'IAuthenticationPlugin',
            'IChallengePlugin',
            'IExtractionPlugin',
        ])
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual('https://cas.server.local', api_client.contents.get(u'cas_url'))

    @restapi
    def test_config_contains_oneoffixx_settings(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@config')
        self.assertEqual(api_client.status_code, 200)
        expected_oneoffixx_settings = {u'baseurl': u'', u'fake_sid': u'', u'double_encode_bug': True}
        oneoffixx_settings = api_client.contents.get('oneoffixx_settings')
        self.assertEqual(expected_oneoffixx_settings, oneoffixx_settings)
