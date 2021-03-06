from collections import OrderedDict
from contextlib import contextmanager
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution
import os


class TestConfigurationAdapter(IntegrationTestCase):

    def test_configuration(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('admin_unit', 'plone'),
            ('org_unit', 'fa'),
            ('current_user', OrderedDict([
                ('username', 'kathi.barfuss'),
                ('description', None),
                ('roles', ['Member']),
                ('home_page', None),
                ('roles_and_principals', ['principal:kathi.barfuss',
                                          'Member',
                                          'Authenticated',
                                          'principal:AuthenticatedUsers',
                                          'principal:fa_users',
                                          'Anonymous']),
                ('email', u'kathi.barfuss@gever.local'),
                ('location', None),
                ('portrait', None),
                ('fullname', u'B\xe4rfuss K\xe4thi'),
                ('@id', 'http://nohost/plone/@users/kathi.barfuss'),
                ('id', 'kathi.barfuss')])),
            ('max_dossier_levels', 2),
            ('max_repositoryfolder_levels', 3),
            ('recently_touched_limit', 10),
            ('document_preserved_as_paper_default', True),
            ('usersnap_api_key', ''),
            ('nightly_jobs', OrderedDict([
                ('start_time', u'1:00:00'),
                ('end_time', u'5:00:00'),
                ])),
            ('oneoffixx_settings', OrderedDict([
                ('fake_sid', u''),
                ('double_encode_bug', True),
                ('cache_timeout', 2592000),
                ('scope', u'oo_V1WebApi'),
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
            ('features', OrderedDict([
                ('activity', False),
                ('archival_file_conversion', False),
                ('archival_file_conversion_blacklist', []),
                ('changed_for_end_date', True),
                ('contacts', False),
                ('disposition_disregard_retention_period', False),
                ('disposition_transport_filesystem', False),
                ('disposition_transport_ftps', False),
                ('doc_properties', False),
                ('dossier_templates', False),
                ('ech0147_export', False),
                ('ech0147_import', False),
                ('favorites', True),
                ('gever_ui_enabled', False),
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
                ('workspace', False),
                ('workspace_client', False),
                ('workspace_meetings', True),
                ('workspace_todo', True),
                ('private_tasks', True),
                ('optional_task_permissions_revoking', False),
                ])),
            ('root_url', 'http://nohost/plone'),
            ('portal_url', 'http://nohost/portal'),
            ('cas_url', None),
            ('apps_url', None),
            ('application_type', 'gever'),
            ('bumblebee_notifications_url', 'http://bumblebee.local/YnVtYmxlYmVl/api/notifications'),
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
            ('is_readonly', False),
            ])

        with custom_apps_url('http://example.com/api/apps'):
            configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(configuration, expected_configuration)
