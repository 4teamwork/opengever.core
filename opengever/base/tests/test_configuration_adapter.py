from collections import OrderedDict
from opengever.base.interfaces import IGeverSettings
from opengever.testing import IntegrationTestCase


class TestConfigurationAdapter(IntegrationTestCase):
    def test_configuration(self):
        expected_configuration = OrderedDict([
            ('@id', 'http://nohost/plone/@config'),
            ('max_dossier_levels', 2),
            ('max_repositoryfolder_levels', 3),
            ('features', OrderedDict([
                ('activity', False),
                ('contacts', False),
                ('doc_properties', False),
                ('dossier_templates', False),
                ('ech0147_export', False),
                ('ech0147_import', False),
                ('favorites', False),
                ('meetings', False),
                ('officeatwork', False),
                ('officeconnector_attach', False),
                ('officeconnector_checkout', False),
                ('preview_auto_refresh', False),
                ('preview_open_pdf_in_new_window', False),
                ('preview', False),
                ('repositoryfolder_documents_tab', True),
                ('repositoryfolder_tasks_tab', True),
                ('solr', False),
                ('word_meetings', False),
                ('workspace', False),
                ])),
            ])
        configuration = IGeverSettings(self.portal).get_config()
        self.assertEqual(configuration, expected_configuration)
