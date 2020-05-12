from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import parse_args
from opengever.bundle.tests.base import BaseTestOggBundleFactory
from os.path import join as pjoin
from pkg_resources import resource_filename
import json
import os


class TestOggBundleFactoryFilesystem(BaseTestOggBundleFactory):

    def test_partial_bundle_factory(self):
        input_path = resource_filename('opengever.bundle.tests',
                                       'assets/basic_import_dossier')

        args = parse_args([input_path,
                           self.tempdir,
                           '--dossier-responsible', 'Test User',
                           '--import-repository-reference', '1', '2', '3'])

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

        # When generating a partial bundle, only contentish items should be
        # generated, no repository root or folder
        self.assertEqual([], reporoot_json)
        self.assertEqual([], repofolders_json)

        # Assert that basic properties are set properly on the different
        # portal types
        self.assertEqual(3, len(dossiers_json))
        for dossier in dossiers_json:
            self.assert_dossier_default_properties(dossier, 'Test User')

        self.assertEqual(2, len(documents_json))
        for document in documents_json:
            self.assert_document_default_properties(document)

        # Assert that the structure was generated correctly
        root_dossier = self.find_item_by_title(dossiers_json, u'Biogeographie')
        self.assertIsNotNone(root_dossier)
        self.assertEqual([[1, 2, 3]], root_dossier[u'parent_reference'])
        self.assertEqual(None, root_dossier[u'parent_guid'])

        in_dossier = self.find_items_by_parent_guid(dossiers_json, root_dossier['guid'])
        self.assertEqual(2, len(in_dossier))

        subdossier = self.find_item_by_title(in_dossier, 'Geobotanik')
        self.assertIsNotNone(subdossier)

        dossiers_in_subdossier = self.find_items_by_parent_guid(dossiers_json, subdossier['guid'])
        self.assertEqual([], dossiers_in_subdossier)

        # there should be no further dossier in the subdossier, but there should be a document
        dossiers_in_subdossier = self.find_items_by_parent_guid(dossiers_json, subdossier['guid'])
        self.assertEqual(0, len(dossiers_in_subdossier),
                         msg="subdossier should not contain any further dossier")
        documents_in_subdossier = self.find_items_by_parent_guid(documents_json, subdossier['guid'])
        self.assertEqual(1, len(documents_in_subdossier),
                         msg="subdossier should contain a document")

        document = self.find_item_by_title(documents_in_subdossier, 'Pflanzensippe.docx')
        self.assertEqual(pjoin(input_path, root_dossier['title'], subdossier['title'], document['title']),
                         document['filepath'])

    def test_full_bundle_factory(self):
        input_path = resource_filename('opengever.bundle.tests',
                                       'assets/basic_import_repository')
        args = parse_args([input_path,
                           self.tempdir,
                           '--dossier-responsible', 'Test User',
                           '--repo-nesting-depth', '3',
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

        self.assertEqual(6, len(dossiers_json))
        for dossier in dossiers_json:
            self.assert_dossier_default_properties(dossier, 'Test User')

        self.assertEqual(4, len(documents_json))
        for document in documents_json:
            self.assert_document_default_properties(document)

        # Assert that the structure was generated correctly
        root = self.find_item_by_title(reporoot_json, 'basic_import_repository')
        self.assertIsNotNone(root)

        in_root = self.find_items_by_parent_guid(repofolders_json, root['guid'])
        self.assertEqual(2, len(in_root))
        self.assertItemsEqual(['Sport', 'Geographie'],
                              [item['title_de'] for item in in_root])

        branch = self.find_item_by_title(in_root, 'Geographie')
        self.assertIsNotNone(branch)
        self.assertEqual(u'repositoryfolder-state-active', branch['review_state'])

        in_branch = self.find_items_by_parent_guid(repofolders_json, branch['guid'])
        self.assertEqual(1, len(in_branch))
        self.assertItemsEqual([u'Geographie nach Fachgebiet'],
                              [item['title_de'] for item in in_branch])

        subbranch = self.find_item_by_title(in_branch, u'Geographie nach Fachgebiet')
        self.assertIsNotNone(subbranch)

        in_subbranch = self.find_items_by_parent_guid(repofolders_json, subbranch['guid'])
        self.assertEqual(2, len(in_subbranch))
        self.assertItemsEqual([u'Geschichte der Geographie',
                               u'Allgemeine Geographie'],
                              [item['title_de'] for item in in_subbranch])

        leaf = self.find_item_by_title(in_subbranch, u'Allgemeine Geographie')
        self.assertIsNotNone(leaf)

        repos_in_leaf = self.find_items_by_parent_guid(repofolders_json, leaf['guid'])
        self.assertEqual([], repos_in_leaf, msg="Leaf should not contain any further repo")
        dossiers_in_leaf = self.find_items_by_parent_guid(dossiers_json, leaf['guid'])
        self.assertEqual(1, len(dossiers_in_leaf), msg="Leaf should not contain a dossier")

        dossier = self.find_item_by_title(dossiers_in_leaf, 'Physische Geographie')
        self.assertIsNotNone(dossier)
        self.assertEqual('dossier-state-active', dossier['review_state'])

        in_dossier = self.find_items_by_parent_guid(dossiers_json, dossier['guid'])
        self.assertEqual(1, len(in_dossier))

        subdossier = self.find_item_by_title(in_dossier, 'Biogeographie')
        self.assertIsNotNone(subdossier)

        in_subdossier = self.find_items_by_parent_guid(dossiers_json, subdossier['guid'])
        self.assertEqual(2, len(in_subdossier))

        subsubdossier = self.find_item_by_title(in_subdossier, 'Invasionsbiologie')
        self.assertIsNotNone(subsubdossier)

        # there should be no further dossier in the subsubdossier, but there should be a document
        dossiers_in_subsubdossier = self.find_items_by_parent_guid(dossiers_json, subsubdossier['guid'])
        self.assertEqual(0, len(dossiers_in_subsubdossier),
                         msg="subsubdossier should not contain any further dossier")
        documents_in_subsubdossier = self.find_items_by_parent_guid(documents_json, subsubdossier['guid'])
        self.assertEqual(1, len(documents_in_subsubdossier),
                         msg="subsubdossier should contain a document")

        document = self.find_item_by_title(documents_in_subsubdossier, 'Pflanzensippe.docx')
        self.assertIsNotNone(document)
