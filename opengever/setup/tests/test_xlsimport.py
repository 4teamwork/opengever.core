from opengever.setup.sections.xlssource import XlsSource
from pkg_resources import resource_filename
from unittest import TestCase


class TextXLSImport(TestCase):

    def setUp(self):
        super(TextXLSImport, self).setUp()

        xls_directory = resource_filename('opengever.setup.tests', 'assets')

        self.source = list(XlsSource(
            None, '', {'directory': xls_directory, 'client_id': 'test'}, []))

    def test_first_type_is_reporoot(self):
        self.assertEquals(u'opengever.repository.repositoryroot',
                          self.source[0]['_type'])

    def test_following_types_are_repofolders(self):
        self.assertEquals(u'opengever.repository.repositoryfolder',
                          self.source[1]['_type'])
        self.assertEquals(u'opengever.repository.repositoryfolder',
                          self.source[2]['_type'])

    def test_empty_key_is_skipped(self):

        self.assertEquals(sorted(
            [u'valid_until',
             u'reference_number',
             u'_repo_root_id',
             u'_type',
             u'valid_from',
             u'responsible_org_unit',
             u'description',
             u'classification',
             u'privacy_layer',
             u'custody_period',
             u'retention_period_annotation',
             u'reactivate_dossiers_access',
             u'read_dossiers_access',
             u'close_dossiers_access',
             u'manage_dossiers_access',
             u'addable_dossier_types',
             u'retention_period',
             u'edit_dossiers_access',
             u'archival_value_annotation',
             u'public_trial',
             u'add_dossiers_access',
             u'block_inheritance',
             u'archival_value',
             u'effective_title']),
            sorted(self.source[1].keys())
        )

    def test_empty_values_for_inheriting_fields_are_skipped(self):
        inherting_fields = ['classification',
                            'privacy_layer',
                            'public_trial',
                            'retention_period',
                            'custody_period',
                            'archival_value']

        for field in inherting_fields:
            self.assertIn(field, self.source[2].keys())
            self.assertNotIn(field, self.source[3].keys())

    def test_valid_from_and_until_are_none_when_not_set(self):
        self.assertEquals(None, self.source[3]['valid_from'])
        self.assertEquals(None, self.source[3]['valid_until'])

    def test_addable_dossier_types_gets_splitted_by_comma(self):
        self.assertEquals(['opengever.dossier.special1',
                           'opengever.dossier.special2'],
                          self.source[0]['addable_dossier_types'])

    def test_archival_value_mapping(self):
        self.assertEquals('unchecked', self.source[0]['archival_value'])
        self.assertEquals('prompt', self.source[1]['archival_value'])

    def test_mapping_handles_values_that_are_already_valid_terms(self):
        self.assertEquals('archival worthy', self.source[2]['archival_value'])

    def test_classification_mapping(self):
        self.assertEquals('confidential', self.source[1]['classification'])

    def test_privacy_layer_mapping(self):
        self.assertEquals('privacy_layer_yes', self.source[2]['privacy_layer'])

    def test_public_trial_mapping(self):
        self.assertEquals('public', self.source[1]['public_trial'])

    def test_xlssouce_can_handle_unicode_titles(self):
        self.assertEquals(self.source[0]['effective_title'],
                          'Ordnungssystem')
        self.assertEquals(self.source[1]['effective_title'],
                          u'F\xfchrung')

    def test_responsible_org_unit_is_imported(self):
        self.assertEquals('EinAmt',
                          self.source[1]['responsible_org_unit'])

    def test_block_inheritance_mapping(self):
        self.assertEquals(self.source[0]['block_inheritance'], True)
        self.assertEquals(self.source[1]['block_inheritance'], False)
        self.assertEquals(self.source[2]['block_inheritance'], True)
