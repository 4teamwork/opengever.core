from tempfile import mkdtemp
from unittest import TestCase
import shutil


class BaseTestOggBundleFactory(TestCase):

    def setUp(self):
        super(BaseTestOggBundleFactory, self).setUp()
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        super(BaseTestOggBundleFactory, self).tearDown()

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
