from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import parse_args
from opengever.bundle.tests import assets
from opengever.bundle.tests.base import BaseTestOggBundleFactory
import json
import os


class TestOggBundleFactoryXLSX(BaseTestOggBundleFactory):

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
