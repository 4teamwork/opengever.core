from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import parse_args
from opengever.bundle.tests import assets
from opengever.bundle.tests.base import BaseTestOggBundleFactory
from opengever.bundle.xlsx import InvalidXLSXException
import json
import os


class TestOggBundleFactoryXLSX(BaseTestOggBundleFactory):

    def test_xlsx_bundle_factory_fails_with_grouped_by_three(self):
        input_path = assets.get_path('invalid_repository_grouped_by_three.xlsx')

        args = parse_args([input_path,
                           self.tempdir,
                           '--users-group', 'Test group'])

        with self.assertRaises(InvalidXLSXException):
            factory = BundleFactory(args)
            factory.dump_bundle()

    def test_xlsx_bundle_factory_fails_with_invalid_parents(self):
        input_path = assets.get_path('invalid_repository_missing_parent.xlsx')

        args = parse_args([input_path,
                           self.tempdir,
                           '--users-group', 'Test group'])

        with self.assertRaises(InvalidXLSXException):
            factory = BundleFactory(args)
            factory.dump_bundle()

    def test_xlsx_bundle_factory(self):
        input_path = assets.get_path('basic_repository.xlsx')

        args = parse_args([input_path,
                           self.tempdir,
                           '--users-group', 'Test group'])

        factory = BundleFactory(args)
        factory.dump_bundle()

        # Check that factory created a directory containing the json files
        generated_dirs = os.listdir(self.tempdir)
        self.assertEqual(1, len(generated_dirs), msg='Should generate one bundle')

        bundle_path = os.path.join(self.tempdir, generated_dirs[0])
        generated_files = os.listdir(bundle_path)
        self.assertItemsEqual(['reporoots.json', 'repofolders.json',
                               'documents.json', 'dossiers.json'],
                              generated_files)

        # load the json files
        with open(os.path.join(bundle_path, 'reporoots.json'), 'r') as infile:
            reporoot_json = json.load(infile)

        with open(os.path.join(bundle_path, 'repofolders.json'), 'r') as infile:
            repofolders_json = json.load(infile)

        with open(os.path.join(bundle_path, 'dossiers.json'), 'r') as infile:
            dossiers_json = json.load(infile)

        with open(os.path.join(bundle_path, 'documents.json'), 'r') as infile:
            documents_json = json.load(infile)

        # Assert that basic properties are set properly on the different
        # portal types
        self.assertEqual(1, len(reporoot_json))
        for reporoot in reporoot_json:
            self.assert_reporoot_default_properties(reporoot, 'Test group')

        self.assertEqual(7, len(repofolders_json))
        for repofolder in repofolders_json:
            self.assert_repofolder_default_properties(repofolder)

        self.assertEqual(0, len(dossiers_json))
        self.assertEqual(0, len(documents_json))

        # Assert that the structure was generated correctly
        root = self.find_item_by_title(reporoot_json, u'Ordnungssystem')
        self.assertIsNotNone(root)
        self.assertEqual(u'Syst\xe8me de classement', root['title_fr'])
        self.assertEqual(u'Repository', root['title_en'])
        self.assertEqual(u'2000-01-01', root['valid_from'])
        self.assertEqual(u'2099-12-31', root['valid_until'])

        in_root = self.find_items_by_parent_guid(repofolders_json, root['guid'])
        self.assertEqual(3, len(in_root))
        self.assertItemsEqual([u'F\xfchrung',
                               u'Bev\xf6lkerung und Sicherheit',
                               u'Finanzen'],
                              [item['title_de'] for item in in_root])

        branch = self.find_item_by_title(in_root, u'F\xfchrung')
        self.assertIsNotNone(branch)
        self.assert_repofolder_default_properties(branch)
        self.assertEqual(u'repositoryfolder-state-active', branch['review_state'])
        self.assertEqual(u'leadership', branch['title_fr'])
        self.assertEqual(u'leadership', branch['title_en'])
        self.assertNotIn('valid_from', branch)
        self.assertNotIn('valid_until', branch)
        self.assertNotIn('description', branch)
        self.assertEqual(u'unprotected', branch['classification'])
        self.assertEqual(u'privacy_layer_no', branch['privacy_layer'])
        self.assertEqual(25, branch['retention_period'])
        self.assertNotIn('retention_period_annotation', branch)
        self.assertEqual('unchecked', branch['archival_value'])
        self.assertNotIn('archival_value_annotation', branch)
        self.assertNotIn('custody_period', branch)

        in_branch = self.find_items_by_parent_guid(repofolders_json, branch['guid'])
        self.assertEqual(3, len(in_branch))
        self.assertItemsEqual([u'Gemeinderecht',
                               u'Vertr\xe4ge und Vereinbarungen',
                               u'Stimmrecht'],
                              [item['title_de'] for item in in_branch])

        subbranch = self.find_item_by_title(in_branch, u'Vertr\xe4ge und Vereinbarungen')
        self.assertIsNotNone(subbranch)
        self.assert_repofolder_default_properties(subbranch)
        self.assertEqual(u'repositoryfolder-state-active', subbranch['review_state'])
        self.assertEqual(u'Contrats et accords', subbranch['title_fr'])
        self.assertEqual(u'Contracts and agreements', subbranch['title_en'])
        self.assertNotIn('valid_from', subbranch)
        self.assertNotIn('valid_until', subbranch)
        self.assertNotIn('description', subbranch)
        self.assertEqual(u'unprotected', subbranch['classification'])
        self.assertEqual(u'privacy_layer_yes', subbranch['privacy_layer'])
        self.assertEqual(25, subbranch['retention_period'])
        self.assertEqual(u'Behalten bitte!', subbranch['retention_period_annotation'])
        self.assertEqual(u'archival worthy', subbranch['archival_value'])
        self.assertEqual(u'Wichtig', subbranch['archival_value_annotation'])
        self.assertEqual(150, subbranch['custody_period'])

        repos_in_branch = self.find_items_by_parent_guid(repofolders_json, subbranch['guid'])
        self.assertEqual(0, len(repos_in_branch),
                         msg="subbranch should not contain any further repos")

    def test_xlsx_bundle_factory_supports_german_only(self):
        input_path = assets.get_path('basic_repository_de_only.xlsx')

        args = parse_args([input_path,
                           self.tempdir,
                           '--users-group', 'Test group'])

        factory = BundleFactory(args)
        factory.dump_bundle()

        # Check that factory created a directory containing the json files
        generated_dirs = os.listdir(self.tempdir)
        self.assertEqual(1, len(generated_dirs), msg='Should generate one bundle')

        bundle_path = os.path.join(self.tempdir, generated_dirs[0])
        generated_files = os.listdir(bundle_path)
        self.assertItemsEqual(['reporoots.json', 'repofolders.json',
                               'documents.json', 'dossiers.json'],
                              generated_files)

        # load the json files
        with open(os.path.join(bundle_path, 'reporoots.json'), 'r') as infile:
            reporoot_json = json.load(infile)

        with open(os.path.join(bundle_path, 'repofolders.json'), 'r') as infile:
            repofolders_json = json.load(infile)

        with open(os.path.join(bundle_path, 'dossiers.json'), 'r') as infile:
            dossiers_json = json.load(infile)

        with open(os.path.join(bundle_path, 'documents.json'), 'r') as infile:
            documents_json = json.load(infile)

        # Assert that basic properties are set properly on the different
        # portal types
        self.assertEqual(1, len(reporoot_json))
        for reporoot in reporoot_json:
            self.assert_reporoot_default_properties(reporoot, 'Test group')

        self.assertEqual(2, len(repofolders_json))
        for repofolder in repofolders_json:
            self.assert_repofolder_default_properties(repofolder)

        self.assertEqual(0, len(dossiers_json))
        self.assertEqual(0, len(documents_json))

        # Assert that the structure was generated correctly
        root = self.find_item_by_title(reporoot_json, u'Ordnungssystem')
        self.assertIsNotNone(root)
        self.assertEqual(u'Ordnungssystem', root['title_de'])
        self.assertEqual(None, root['title_en'])
        self.assertEqual(None, root['title_fr'])
        self.assertEqual(u'2000-01-01', root['valid_from'])
        self.assertEqual(u'2099-12-31', root['valid_until'])

        in_root = self.find_items_by_parent_guid(repofolders_json, root['guid'])
        self.assertEqual(1, len(in_root))

        branch = self.find_item_by_title(in_root, u'F\xfchrung')
        self.assertIsNotNone(branch)
        self.assert_repofolder_default_properties(branch)
        self.assertEqual(u'F\xfchrung', branch['title_de'])
        self.assertNotIn('title_fr', branch)
        self.assertNotIn('title_en', branch)

        in_branch = self.find_items_by_parent_guid(repofolders_json, branch['guid'])
        self.assertEqual(1, len(in_branch))

        subbranch = self.find_item_by_title(in_branch, u'Gemeinderecht')
        self.assertIsNotNone(subbranch)
        self.assert_repofolder_default_properties(subbranch)
        self.assertEqual(u'Gemeinderecht', subbranch['title_de'])
        self.assertNotIn('title_fr', subbranch)
        self.assertNotIn('title_en', subbranch)
        self.assertEqual(25, subbranch['retention_period'])

    def test_xlsx_bundle_factory_supports_permissions(self):
        input_path = assets.get_path('basic_repository_permissions.xlsx')

        args = parse_args([input_path, self.tempdir])

        factory = BundleFactory(args)
        factory.dump_bundle()

        # Check that factory created a directory containing the json files
        generated_dirs = os.listdir(self.tempdir)
        self.assertEqual(1, len(generated_dirs), msg='Should generate one bundle')

        bundle_path = os.path.join(self.tempdir, generated_dirs[0])

        with open(os.path.join(bundle_path, 'reporoots.json'), 'r') as infile:
            reporoot_json = json.load(infile)

        with open(os.path.join(bundle_path, 'repofolders.json'), 'r') as infile:
            repofolders_json = json.load(infile)

        self.assertEqual(
            {
                u'add': [u'og_demo-ftw_users'],
                u'block_inheritance': False,
                u'close': [u'og_demo-ftw_users'],
                u'edit': [u'og_demo-ftw_users'],
                u'manage_dossiers': [u'og_demo-ftw_users'],
                u'reactivate': [u'og_demo-ftw_users'],
                u'read': [u'og_demo-ftw_users'],
            },
            reporoot_json[0]['_permissions']
        )

        self.assertEqual(
            {
                u'add': [],
                u'block_inheritance': False,
                u'close': [],
                u'edit': [],
                u'manage_dossiers': [],
                u'reactivate': [],
                u'read': [],
            },
            repofolders_json[0]['_permissions']
        )
        self.assertEqual(
            {
                u'add': [u'og_contributors'],
                u'block_inheritance': True,
                u'close': [u'og_resolvers'],
                u'edit': [u'og_editors'],
                u'manage_dossiers': [u'og_managers'],
                u'reactivate': [u'og_reactivators'],
                u'read': [u'og_readers'],
            },
            repofolders_json[1]['_permissions']
        )
