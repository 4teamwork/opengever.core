from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import parse_args
from opengever.bundle.tests import assets
from tempfile import mkdtemp
from unittest import TestCase
import json
import os
import shutil


class TestOggBundleFactoryXLSX(TestCase):

    def setUp(self):
        super(TestOggBundleFactoryXLSX, self).setUp()
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        super(TestOggBundleFactoryXLSX, self).tearDown()

    def find_item_by_title(self, items, title):
        for item in items:
            if item.get('title') or item.get('title_de') == title:
                return item
        return None

    def find_items_by_parent_guid(self, items, value):
        matching_items = []
        for item in items:
            if item.get('parent_guid') == value:
                matching_items.append(item)
        return matching_items

    def assert_reporoot_default_properties(self, reporoot, user_group):
        # Title should be stored with the title_de (and not title) key
        self.assertIn('title_de', reporoot)
        self.assertNotIn('title', reporoot)
        self.assertTrue(reporoot.get('title_de'))

        self.assertEqual('repositoryroot-state-active', reporoot['review_state'],
                         msg="Review state should be set to active")

        # Permissions are set on the repository root
        self.assertDictEqual({u'read': [user_group],
                              u'edit': [user_group],
                              u'add': [user_group],
                              u'close': [],
                              u'reactivate': []},
                             reporoot['_permissions'])

        self.assertFalse(reporoot.get(u'parent_guid') or reporoot.get(u'parent_reference'),
                         msg="A reporoot cannot define a parent")

    def assert_repofolder_default_properties(self, repofolder):
        # Title should be stored with the title_de (and not title) key
        self.assertIn('title_de', repofolder)
        self.assertNotIn('title', repofolder)
        self.assertTrue(repofolder.get('title_de'))

        self.assertEqual('repositoryfolder-state-active', repofolder['review_state'],
                         msg="Review state should be set to active")

        self.assertTrue(repofolder.get(u'parent_guid') or repofolder.get(u'parent_reference'),
                        msg="A repofolder always needs to define its parent")

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
        root = self.find_item_by_title(reporoot_json, u'Ordnungssysteme')
        self.assertIsNotNone(root)

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

        repos_in_branch = self.find_items_by_parent_guid(repofolders_json, subbranch['guid'])
        self.assertEqual(0, len(repos_in_branch),
                         msg="subbranch should not contain any further repos")
