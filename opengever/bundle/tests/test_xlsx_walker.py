from unittest import TestCase
from opengever.bundle.xlsx import XLSXWalker
from opengever.bundle.tests import assets


class TestXLSXWalker(TestCase):

    maxDiff = None

    def test_xlsx_walker_walk(self):
        walker = XLSXWalker(assets.get_path('basic_repository.xlsx'))
        items = list(walker.walk())

        self.assertEqual([
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryroot',
             u'add_dossiers_access': u'og_demo-ftw_users',
             u'archival_value_annotation': u'',
             u'close_dossiers_access': u'og_demo-ftw_users',
             u'description': u'',
             u'edit_dossiers_access': u'og_demo-ftw_users',
             u'effective_title': u'Ordnungssysteme',
             u'effective_title_fr': u'Syst\xe8me de classement',
             u'manage_dossiers_access': u'og_demo-ftw_users',
             u'reactivate_dossiers_access': u'og_demo-ftw_users',
             u'read_dossiers_access': u'og_demo-ftw_users',
             u'reference_number': u'',
             u'retention_period_annotation': u'',
             u'valid_from': '2000-01-01',
             u'valid_until': '2099-12-31'},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value': u'unchecked',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'F\xfchrung',
             u'effective_title_fr': u'leadership',
             u'manage_dossiers_access': u'',
             u'privacy_layer': 'privacy_layer_no',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'0',
             u'retention_period': 25,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Gemeinderecht',
             u'effective_title_fr': u'droit municipal',
             u'manage_dossiers_access': u'',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'0.0',
             u'retention_period': 25,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value': u'archival worthy',
             u'archival_value_annotation': u'Wichtig',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'custody_period': 150,
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Vertr\xe4ge und Vereinbarungen',
             u'effective_title_fr': u'Contrats et accords',
             u'manage_dossiers_access': u'',
             u'privacy_layer': 'privacy_layer_yes',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'0.1',
             u'retention_period': 25,
             u'retention_period_annotation': u'Behalten bitte!',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Stimmrecht',
             u'effective_title_fr': u'droit de vote',
             u'manage_dossiers_access': u'',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'0.2',
             u'retention_period': 10,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Bev\xf6lkerung und Sicherheit',
             u'effective_title_fr': u'Population et de la s\xe9curit\xe9',
             u'manage_dossiers_access': u'',
             u'privacy_layer': 'privacy_layer_no',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'1',
             u'retention_period': 15,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Einwohnerkontrolle',
             u'effective_title_fr': u'r\xe9sidents',
             u'manage_dossiers_access': u'',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'1.0',
             u'retention_period': 20,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None},
            {'_repo_root_id': 'basic_repository.xlsx',
             '_type': u'opengever.repository.repositoryfolder',
             u'add_dossiers_access': u'',
             u'archival_value': u'archival worthy with sampling',
             u'archival_value_annotation': u'',
             u'classification': 'unprotected',
             u'close_dossiers_access': u'',
             u'custody_period': 30,
             u'description': u'',
             u'edit_dossiers_access': u'',
             u'effective_title': u'Finanzen',
             u'effective_title_fr': u'finances',
             u'manage_dossiers_access': u'',
             u'reactivate_dossiers_access': u'',
             u'read_dossiers_access': u'',
             u'reference_number': u'9',
             u'retention_period': 25,
             u'retention_period_annotation': u'',
             u'valid_from': None,
             u'valid_until': None}
            ], items)

    def test_xlsx_walker_iter_and_node_initialization(self):
        walker = XLSXWalker(assets.get_path('basic_repository.xlsx'))
        items = list(walker)

        self.assertEqual(8, len(items))

        root = items[0]
        self.assertIsNone(root.creation_date)
        self.assertIsNone(root.modification_date)
        self.assertEqual(0, root.level)
        self.assertIsNone(root.reference_number)
        self.assertIsNone(root.reference_number_prefix)
        self.assertIsNone(root.parent_reference_number)
        self.assertIsNotNone(root.guid)
        self.assertTrue(root.guid.startswith('ROOT-Ordnungssysteme-'), root.guid)
        self.assertIsNone(root.parent_guid)
        self.assertEqual(u'Ordnungssysteme', root.title)

        repo = items[1]
        self.assertIsNone(repo.creation_date)
        self.assertIsNone(repo.modification_date)
        self.assertEqual(1, repo.level)
        self.assertEqual(u'0', repo.reference_number)
        self.assertEqual(u'0', repo.reference_number_prefix)
        self.assertIsNone(repo.parent_reference_number)
        self.assertIsNotNone(repo.guid)
        self.assertTrue(repo.guid.startswith('0-Fuehrung-'), repo.guid)
        self.assertEqual(root.guid, repo.parent_guid)
        self.assertEqual(u'F\xfchrung', repo.title)

        # purposefully test the 2nd subrepo to have different reference numbers
        # from repo
        subrepo = items[3]
        self.assertIsNone(subrepo.creation_date)
        self.assertIsNone(subrepo.modification_date)
        self.assertEqual(2, subrepo.level)
        self.assertEqual(u'0.1', subrepo.reference_number)
        self.assertEqual(u'1', subrepo.reference_number_prefix)
        self.assertEqual(u'0', subrepo.parent_reference_number)
        self.assertIsNotNone(subrepo.guid)
        self.assertTrue(subrepo.guid.startswith('0.1-Vertraege und Vereinbarungen-'),
                        subrepo.guid)
        self.assertEqual(repo.guid, subrepo.parent_guid)
        self.assertEqual(u'Vertr\xe4ge und Vereinbarungen', subrepo.title)
