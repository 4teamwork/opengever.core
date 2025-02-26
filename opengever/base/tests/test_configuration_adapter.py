from collections import OrderedDict
from contextlib import contextmanager
from opengever.base.interfaces import IGeverSettings
from opengever.kub.interfaces import IKuBSettings
from opengever.ris.interfaces import IRisSettings
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution
from plone import api
import os


class TestConfigurationAdapter(IntegrationTestCase):

    def setUp(self):
        super(TestConfigurationAdapter, self).setUp()
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee.local/'
        api.portal.set_registry_record('base_url', u'http://localhost:3000', IRisSettings)

    def test_configuration(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('admin_unit', 'plone'),
            ('org_unit', 'fa'),
            ('current_user', OrderedDict([
                ('username', self.regular_user.getUserName()),
                ('description', None),
                ('roles', ['Member', 'WorkspaceClientUser']),
                ('home_page', None),
                ('roles_and_principals', ['principal:%s' % self.regular_user.id,
                                          'Member',
                                          'WorkspaceClientUser',
                                          'Authenticated',
                                          'principal:AuthenticatedUsers',
                                          'principal:projekt_a',
                                          'principal:fa_users',
                                          'Anonymous']),
                ('email', u'foo@example.com'),
                ('location', None),
                ('portrait', None),
                ('fullname', u'B\xe4rfuss K\xe4thi'),
                ('@id', 'http://nohost/plone/@users/%s' % self.regular_user.id),
                ('id', self.regular_user.id)])),
            ('max_dossier_levels', 2),
            ('max_repositoryfolder_levels', 3),
            ('recently_touched_limit', 10),
            ('document_preserved_as_paper_default', True),
            ('nightly_jobs', OrderedDict([
                ('start_time', u'1:00:00'),
                ('end_time', u'5:00:00'),
                ])),
            ('user_settings', OrderedDict([
                ('notify_inbox_actions', True),
                ('notify_own_actions', False),
                ('seen_tours', ['*']),
            ])),
            ('sharing_configuration', OrderedDict([
                ('white_list_prefix', u'^.+'),
                ('black_list_prefix', u'^$'),
                ])),
            ('p7m_extension_replacement', 'eml'),
            ('features', OrderedDict([
                ('activity', False),
                ('archival_file_conversion', False),
                ('archival_file_conversion_blacklist', []),
                ('changed_for_end_date', True),
                ('classic_ui_enabled', True),
                ('contacts', 'plone'),
                ('disposition_disregard_retention_period', False),
                ('disposition_transport_filesystem', False),
                ('disposition_transport_ftps', False),
                ('doc_properties', False),
                ('dossier_checklist', False),
                ('dossier_templates', False),
                ('dossier_transfers', False),
                ('ech0147_export', False),
                ('ech0147_import', False),
                ('favorites', True),
                ('filing_number', False),
                ('gever_ui_enabled', True),
                ('grant_role_manager_to_responsible', False),
                ('hubspot', False),
                ('journal_pdf', False),
                ('tasks_pdf', False),
                ('meetings', False),
                ('officeatwork', False),
                ('officeconnector_attach', True),
                ('officeconnector_checkout', True),
                ('oneoffixx', False),
                ('preview_auto_refresh', False),
                ('preview_open_pdf_in_new_window', False),
                ('preview', False),
                ('purge_trash', False),
                ('repositoryfolder_documents_tab', True),
                ('repositoryfolder_proposals_tab', True),
                ('repositoryfolder_tasks_tab', True),
                ('resolver_name', 'strict'),
                ('sablon_date_format', u'%d.%m.%Y'),
                ('solr', True),
                ('tasktemplatefolder_nesting', False),
                ('workspace', False),
                ('workspace_invitation', True),
                ('workspace_client', False),
                ('workspace_creation_restricted', False),
                ('workspace_meetings', True),
                ('workspace_todo', True),
                ('private_tasks', True),
                ('optional_task_permissions_revoking', False),
                ('multiple_dossier_types', False),
                ])),
            ('root_url', 'http://nohost/plone'),
            ('portal_url', 'http://nohost/portal'),
            ('cas_url', None),
            ('apps_url', None),
            ('application_type', 'gever'),
            ('bumblebee_notifications_url', 'http://bumblebee.local/YnVtYmxlYmVl/api/notifications'),
            ('ris_base_url', 'http://localhost:3000'),
            ('is_readonly', False),
            ])

        with self.login(self.regular_user):
            configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(expected_configuration, configuration)

    def test_configuration_for_anonymous(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('admin_unit', 'plone'),
            ('org_unit', '__dummy_unit_id__'),
            ('root_url', 'http://nohost/plone'),
            ('portal_url', 'http://nohost/portal'),
            ('cas_url', None),
            ('apps_url', None),
            ('application_type', 'gever'),
            ('bumblebee_notifications_url', 'http://bumblebee.local/YnVtYmxlYmVl/api/notifications'),
            ('ris_base_url', 'http://localhost:3000'),
            ('is_readonly', False),
            ])
        configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(configuration, expected_configuration)

    def test_application_type_is_teamraum_if_workspace_feature_enabled(self):
        self.activate_feature('workspace')
        application_type = IGeverSettings(self.portal).get_application_type()
        self.assertEqual('teamraum', application_type)

    def test_apps_url_can_be_set_through_env_variable(self):

        @contextmanager
        def custom_apps_url(url):
            """Contextmanager to temporary replace the APPS_ENDPOINT_URL
            """
            original_env_value = os.environ.get('APPS_ENDPOINT_URL')
            os.environ['APPS_ENDPOINT_URL'] = url

            yield

            if original_env_value:
                os.environ['APPS_ENDPOINT_URL'] = original_env_value
            else:
                del os.environ['APPS_ENDPOINT_URL']

        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('admin_unit', 'plone'),
            ('org_unit', '__dummy_unit_id__'),
            ('root_url', 'http://nohost/plone'),
            ('portal_url', 'http://nohost/portal'),
            ('cas_url', None),
            ('apps_url', 'http://example.com/api/apps'),
            ('application_type', 'gever'),
            ('bumblebee_notifications_url', 'http://bumblebee.local/YnVtYmxlYmVl/api/notifications'),
            ('ris_base_url', 'http://localhost:3000'),
            ('is_readonly', False),
            ])

        with custom_apps_url('http://example.com/api/apps'):
            configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(configuration, expected_configuration)

    def test_contact_type(self):
        contact_type = IGeverSettings(self.portal)._get_contact_type()
        self.assertEqual("plone", contact_type)

        api.portal.set_registry_record(
            'base_url', u'http://localhost:8000', IKuBSettings)
        contact_type = IGeverSettings(self.portal)._get_contact_type()
        self.assertEqual("kub", contact_type)
