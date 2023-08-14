from ftw.builder import Builder
from ftw.builder import create
from ftw.casauth.plugin import CASAuthenticationPlugin
from ftw.testbrowser import browsing
from mock import patch
from opengever.private import enable_opengever_private
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from pkg_resources import get_distribution
from plone import api
import os


class TestConfig(IntegrationTestCase):

    @property
    def config_url(self):
        return self.portal.absolute_url() + '/@config'

    @browsing
    def test_config_contains_id(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'@id'), self.config_url)

    @browsing
    def test_config_contains_version(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'version'), get_distribution('opengever.core').version)

    @browsing
    def test_config_contains_admin_and_org_unit(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'admin_unit'), 'plone')
        self.assertEqual(browser.json.get(u'org_unit'), 'fa')

    @browsing
    def test_config_contains_userinfo(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json['current_user'].get(u'id'), u'kathi.barfuss')
        self.assertEqual(browser.json['current_user'].get(u'fullname'), u'B\xe4rfuss K\xe4thi')
        self.assertEqual(browser.json['current_user'].get(u'email'), u'foo@example.com')

    @browsing
    def test_config_contains_features(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'features'),
            {
                u'activity': False,
                u'archival_file_conversion': False,
                u'archival_file_conversion_blacklist': [],
                u'changed_for_end_date': True,
                u'contacts': 'plone',
                u'disposition_disregard_retention_period': False,
                u'disposition_transport_filesystem': False,
                u'disposition_transport_ftps': False,
                u'doc_properties': False,
                u'dossier_checklist': False,
                u'dossier_templates': False,
                u'ech0147_export': False,
                u'ech0147_import': False,
                u'favorites': True,
                u'filing_number': False,
                u'gever_ui_enabled': True,
                u'hubspot': False,
                u'journal_pdf': False,
                u'meetings': False,
                u'multiple_dossier_types': False,
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
                u'tasktemplatefolder_nesting': False,
                u'workspace': False,
                u'workspace_client': False,
                u'workspace_creation_restricted': False,
                u'workspace_meetings': True,
                u'workspace_todo': True,
            })

    @browsing
    def test_config_contains_max_subdossier_depth(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_dossier_levels'), 2)

    @browsing
    def test_config_contains_max_repository_depth(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_repositoryfolder_levels'), 3)

    @browsing
    def test_config_contains_recently_touched_limit(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
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
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'cas_url'), 'https://cas.server.local')

    @browsing
    def test_config_contains_portal_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'portal_url'), 'http://nohost/portal')

    @browsing
    def test_config_contains_application_type(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'application_type'), 'gever')

    @browsing
    def test_config_contains_is_readonly_flag(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertFalse(browser.json.get(u'is_readonly'))

        with ZODBStorageInReadonlyMode():
            browser.open(self.config_url, headers=self.api_headers)
            self.assertEqual(200, browser.status_code)
            self.assertTrue(browser.json.get(u'is_readonly'))

    @browsing
    def test_config_contains_oneoffixx_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
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
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'sharing_configuration'),
                         {u'white_list_prefix': '^.+', u'black_list_prefix': '^$'})

    @browsing
    def test_config_contains_user_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url,
                     headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            {u'notify_inbox_actions': True,
             u'notify_own_actions': False,
             u'seen_tours': [u'*']},
            browser.json.get(u'user_settings'))

    @browsing
    def test_config_contains_nightly_job_timewindow_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'nightly_jobs'),
                         {u'start_time': u'1:00:00', u'end_time': u'5:00:00'})

    @browsing
    def test_config_contains_is_emm_environment(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url,
                     headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'is_emm_environment', browser.json)

    @browsing
    def test_is_admin_is_true_for_administrators(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_admin'))

    @browsing
    def test_is_admin_is_true_for_limited_admins(self, browser):
        self.login(self.limited_admin, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_admin'))

    @browsing
    def test_is_admin_is_false_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_admin'))

    @browsing
    def test_is_manager_is_true_for_managers(self, browser):
        self.login(self.manager, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_manager'))

    @browsing
    def test_is_manager_is_false_for_administrators(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_manager'))

    @browsing
    def test_is_manager_is_false_for_limited_admins(self, browser):
        self.login(self.limited_admin, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_manager'))

    @browsing
    def test_is_manager_is_false_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_manager'))

    @browsing
    def test_is_inbox_user_is_true_for_users_assigned_to_the_inbox_group(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_inbox_user'))

    @browsing
    def test_is_inbox_user_is_false_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_inbox_user'))

    @browsing
    def test_is_propertysheets_manager_is_true_for_users_with_manage_propertysheets_permission(self, browser):
        self.login(self.propertysheets_manager, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertTrue(browser.json.get(u'is_propertysheets_manager'))

    @browsing
    def test_is_propertysheets_manager_is_false_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertFalse(browser.json.get(u'is_propertysheets_manager'))

    @browsing
    def test_config_contains_bumblebee_app_id(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
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
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            u'http://nohost/plone/private/kathi.barfuss',
            browser.json.get(u'private_folder_url')
        )

    @browsing
    def test_config_contains_url_to_template_folder(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            u'http://nohost/plone/vorlagen',
            browser.json.get(u'template_folder_url')
        )

    @browsing
    def test_config_contains_current_inbox_url_if_available(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'inbox_folder_url'), u'http://nohost/plone/eingangskorb/eingangskorb_fa')

        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'inbox_folder_url'), u'')

    @browsing
    def test_config_contains_bumblebee_notification_url(self, browser):
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee.local/'

        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'bumblebee_notifications_url'), u'http://bumblebee.local/YnVtYmxlYmVl/api/notifications')

    @browsing
    def test_config_contains_primary_repository(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'primary_repository'), self.repository_root.absolute_url())

        root2 = create(Builder('repository_root').titled(u'Ordnungssystem V2'))

        browser.open(self.config_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'primary_repository'), root2.absolute_url())

    @browsing
    def test_feature_filing_number(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertFalse(browser.json['features']['filing_number'])

        self.activate_feature('filing_number')

        browser.open(self.config_url, headers=self.api_headers)
        self.assertTrue(browser.json['features']['filing_number'])

    @browsing
    def test_feature_multiple_dossier_types(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)
        self.assertFalse(browser.json['features']['multiple_dossier_types'])

        with patch('opengever.base.configuration.count_available_dossier_types', return_value=2):
            browser.open(self.config_url, headers=self.api_headers)
            self.assertTrue(browser.json['features']['multiple_dossier_types'])

    @browsing
    def test_contains_the_current_admin_unit(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.config_url, headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@admin-units/plone',
             u'@type': u'virtual.ogds.admin_unit',
             u'abbreviation': u'Client1',
             u'enabled': True,
             u'hidden': False,
             u'public_url': u'http://nohost/plone',
             u'title': u'Hauptmandant',
             u'unit_id': u'plone',
             u'org_units': [{u'@id': u'http://nohost/plone/@org-units/fa',
                             u'@type': u'virtual.ogds.org_unit',
                             u'enabled': True,
                             u'hidden': False,
                             u'title': u'Finanz\xe4mt',
                             u'unit_id': u'fa'},
                            {u'@id': u'http://nohost/plone/@org-units/rk',
                             u'@type': u'virtual.ogds.org_unit',
                             u'enabled': True,
                             u'hidden': False,
                             u'title': u'Ratskanzl\xc3\xa4i',
                             u'unit_id': u'rk'}]},
            browser.json['current_admin_unit'])
