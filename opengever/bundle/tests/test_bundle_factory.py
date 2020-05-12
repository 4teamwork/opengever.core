from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import get_parser
from opengever.testing import IntegrationTestCase
from os.path import join as pjoin
from pkg_resources import resource_filename
from tempfile import mkdtemp
import json
import os
import shutil


class TestOggBundleFactory(IntegrationTestCase):

    def setUp(self):
        super(TestOggBundleFactory, self).setUp()
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        super(TestOggBundleFactory, self).tearDown()

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

    def assert_dossier_default_properties(self, dossier, responsible):
        # Title should be stored with the title (and not title_de) key
        self.assertIn('title', dossier)
        self.assertNotIn('title_de', dossier)
        self.assertTrue(dossier.get('title'))

        self.assertEqual('dossier-state-active', dossier['review_state'],
                         msg="Review state should be set to active")

        self.assertTrue(dossier.get('responsible'),
                        msg="Dossier responsible always needs to be set")
        self.assertEqual(responsible, dossier['responsible'])

        self.assertTrue(dossier.get(u'parent_guid') or dossier.get(u'parent_reference'),
                        msg="A dossier always needs to define its parent")

    def assert_document_default_properties(self, document):
        # Title should be stored with the title (and not title_de) key
        self.assertIn('title', document)
        self.assertNotIn('title_de', document)
        self.assertTrue(document.get('title'))

        self.assertEqual('document-state-draft', document['review_state'],
                         msg="Review state should be set to draft")

        self.assertTrue(document.get('filepath'),
                        msg="Filepath always needs to be defined")

        self.assertTrue(document.get(u'parent_guid') or document.get(u'parent_reference'),
                        msg="A document always needs to define its parent")

        # We cannot assert the values of the document_date and changed fields
        # as they basically depend on when the repo was cloned. Instead we
        # simply assert the list of properties on the object
        self.assertItemsEqual(
            [u'filepath',
             u'parent_guid',
             u'changed',
             u'document_date',
             u'title',
             u'review_state',
             u'guid'],
            document.keys())

    def test_partial_bundle_factory(self):
        parser = get_parser()
        input_path = resource_filename('opengever.bundle.tests',
                                       'assets/basic_import_dossier')

        args = parser.parse_args([input_path,
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
        parser = get_parser()
        input_path = resource_filename('opengever.bundle.tests',
                                       'assets/basic_import_repository')
        args = parser.parse_args([input_path,
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
