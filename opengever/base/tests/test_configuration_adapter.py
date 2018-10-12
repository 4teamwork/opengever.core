from collections import OrderedDict
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution


class TestConfigurationAdapter(IntegrationTestCase):
    def test_configuration(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('max_dossier_levels', 2),
            ('max_repositoryfolder_levels', 3),
            ('recently_touched_limit', 10),
            ('oneoffixx_settings', OrderedDict([
                ('baseurl', u''),
                ('fake_sid', u''),
                ('double_encode_bug', True),
            ])),
            ('features', OrderedDict([
                ('activity', False),
                ('archival_file_conversion', False),
                ('contacts', False),
                ('doc_properties', False),
                ('dossier_templates', False),
                ('ech0147_export', False),
                ('ech0147_import', False),
                ('favorites', True),
                ('gever_ui_enabled', False),
                ('gever_ui_path', 'http://localhost:8081/#/'),
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
                ('solr', False),
                ('workspace', False),
                ])),
            ('root_url', 'http://nohost/plone'),
            ('cas_url', None),
            ])
        with self.login(self.regular_user):
            configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(expected_configuration, configuration)

    def test_configuration_for_anonymous(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('version', get_distribution('opengever.core').version),
            ('root_url', 'http://nohost/plone'),
            ('cas_url', None),
            ])
        configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(configuration, expected_configuration)
