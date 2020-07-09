from ftw.casauth.plugin import CASAuthenticationPlugin
from ftw.testbrowser import browsing
from opengever.base.interfaces import IUserSnapSettings
from opengever.private import enable_opengever_private
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution
from plone import api


class TestConfig(IntegrationTestCase):

    @browsing
    def test_config_contains_id(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'@id'), url)

    @browsing
    def test_config_contains_version(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'version'), get_distribution('opengever.core').version)

    @browsing
    def test_config_contains_userinfo(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'userid'), u'kathi.barfuss')
        self.assertEqual(browser.json.get(u'user_fullname'), u'B\xe4rfuss K\xe4thi')

    @browsing
    def test_config_contains_features(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'features'),
            {
                u'activity': False,
                u'archival_file_conversion': False,
                u'archival_file_conversion_blacklist': [],
                u'changed_for_end_date': True,
                u'contacts': False,
                u'disposition_transport_filesystem': False,
                u'disposition_transport_ftps': False,
                u'doc_properties': False,
                u'dossier_templates': False,
                u'ech0147_export': False,
                u'ech0147_import': False,
                u'favorites': True,
                u'gever_ui_enabled': False,
                u'journal_pdf': False,
                u'meetings': False,
                u'officeatwork': False,
                u'officeconnector_attach': True,
                u'officeconnector_checkout': True,
                u'oneoffixx': False,
                u'optional_task_permissions_revoking': False,
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
                u'solr': True,
                u'tasks_pdf': False,
                u'workspace': False,
                u'workspace_client': False,
            })

    @browsing
    def test_config_contains_max_subdossier_depth(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_dossier_levels'), 2)

    @browsing
    def test_config_contains_max_repository_depth(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_repositoryfolder_levels'), 3)

    @browsing
    def test_config_contains_recently_touched_limit(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'recently_touched_limit'), 10)

    @browsing
    def test_config_contains_cas_url(self, browser):
        # Install CAS plugin
        uf = self.portal.acl_users
        plugin = CASAuthenticationPlugin(
            'cas_auth', cas_server_url='https://cas.server.local')
        uf._setObject(plugin.getId(), plugin)
        plugin = uf['cas_auth']
        plugin.manage_activateInterfaces([
            'IAuthenticationPlugin',
            'IChallengePlugin',
            'IExtractionPlugin',
        ])

        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'cas_url'), 'https://cas.server.local')

    @browsing
    def test_config_contains_oneoffixx_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config', headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        expected_oneoffixx_settings = {
            u'fake_sid': u'',
            u'double_encode_bug': True,
            u'cache_timeout': 2592000,
            u'scope': u'oo_V1WebApi',
        }
        oneoffixx_settings = browser.json.get('oneoffixx_settings')
        self.assertEqual(expected_oneoffixx_settings, oneoffixx_settings)

    @browsing
    def test_config_contains_sharing_configuration_white_and_black_lists(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'sharing_configuration'),
                         {u'white_list_prefix': '^.+', u'black_list_prefix': '^$'})

    @browsing
    def test_config_contains_user_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            {u'notify_inbox_actions': True,
             u'notify_own_actions': False,
             u'seen_tours': [u'*']},
            browser.json.get(u'user_settings'))

    @browsing
    def test_config_contains_nightly_job_timewindow_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'nightly_jobs'),
                         {u'start_time': u'1:00:00', u'end_time': u'5:00:00'})

    @browsing
    def test_config_contains_is_emm_environment(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'is_emm_environment', browser.json)

    @browsing
    def test_is_admin_menu_visible_is_true_for_administrators(self, browser):
        self.login(self.administrator, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_admin_menu_visible'))

    @browsing
    def test_is_admin_menu_visible_is_false_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_admin_menu_visible'))

    @browsing
    def test_config_contains_bumblebee_app_id(self, browser):
        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            'local',
            browser.json.get(u'bumblebee_app_id')
        )

    @browsing
    def test_config_contains_url_to_private_folder(self, browser):
        # Enable member area creation in Plone.
        membership_tool = api.portal.get_tool('portal_membership')
        enable_opengever_private()
        self.assertTrue(membership_tool.getMemberareaCreationFlag())

        # Create the user's private folder (this is not triggered by
        # authenticating the user, it must be done manually).
        self.login(self.regular_user, browser)
        membership_tool.createMemberarea()

        # Finally test our implementation.
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            u'http://nohost/plone/private/kathi.barfuss',
            browser.json.get(u'private_folder_url')
        )

    @browsing
    def test_config_contains_usersnap_api_key(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal.absolute_url() + '/@config',
                     headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'usersnap_api_key'), u'')

        api.portal.set_registry_record('api_key', u'some key', interface=IUserSnapSettings)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'usersnap_api_key'), u'some key')
