from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from opengever.usermigration.private_folders import PrivateFoldersMigrator
from plone import api
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id


class TestPrivateFoldersMigrator(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFoldersMigrator, self).setUp()
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')
        self.root = create(Builder('private_root')
                           .within(self.portal)
                           .having(id='private'))

        create_members_folder(self.root)

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

        create(Builder('user')
               .with_userid('manager')
               .with_roles('Manager'))

        create(Builder('user')
               .with_userid('HANS.MUSTER')
               .with_roles('Reader', 'Editor', 'Contributor'))

        create(Builder('user')
               .with_userid('hans.muster')
               .with_roles('Reader', 'Editor', 'Contributor'))

    def test_merges_private_folder_contents_into_new_one(self):
        self.login('HANS.MUSTER')
        create_members_folder(self.root)
        private_folder = self.root['HANS.MUSTER']

        dossier = create(Builder('private_dossier')
                         .within(private_folder)
                         .titled(u'Dossier in old private folder'))
        create(Builder('document')
               .within(dossier)
               .titled(u'Doc in old private folder'))

        self.login('hans.muster')
        create_members_folder(self.root)
        new_private_folder = self.root['hans.muster']

        new_dossier = create(Builder('private_dossier')
                             .within(new_private_folder)
                             .titled(u'Dossier in new private folder'))
        create(Builder('document')
               .within(new_dossier)
               .titled(u'Doc in new private folder'))

        self.login('manager')
        results = PrivateFoldersMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(
            [('/plone/private/HANS.MUSTER', 'HANS.MUSTER', 'hans.muster')],
            results['private_folders']['moved'])

        # Old folder shouldn't exist any more
        self.assertEqual(
            [WorkflowPolicyConfig_id, 'test_user_1_', 'hans.muster'],
            self.root.objectIds())

        # New folder should contain all dossiers
        self.assertItemsEqual(
            ['dossier-1', 'dossier-2'], self.root['hans.muster'].objectIds())

        # Old document should be in new location and properly reindexed
        self.assertItemsEqual(
            ['/plone/private/hans.muster/dossier-1/document-1',
             '/plone/private/hans.muster/dossier-2/document-2'],
            [b.getPath() for b in self.catalog(
                portal_type='opengever.document.document')])

    def test_renames_old_private_folder_if_new_one_doesnt_exist(self):
        self.login('HANS.MUSTER')
        create_members_folder(self.root)
        private_folder = self.root['HANS.MUSTER']

        dossier = create(Builder('private_dossier')
                         .within(private_folder)
                         .titled(u'Dossier in old private folder'))
        create(Builder('document')
               .within(dossier)
               .titled(u'Doc in old private folder'))

        self.login('manager')
        results = PrivateFoldersMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(
            [('/plone/private/HANS.MUSTER', 'HANS.MUSTER', 'hans.muster')],
            results['private_folders']['moved'])

        # Old folder shouldn't exist any more
        self.assertEqual(
            [WorkflowPolicyConfig_id, 'test_user_1_', 'hans.muster'],
            self.root.objectIds())

        # New folder should contain dossier
        self.assertItemsEqual(
            ['dossier-1'], self.root['hans.muster'].objectIds())

        # Old document should be in new location and properly reindexed
        self.assertItemsEqual(
            ['/plone/private/hans.muster/dossier-1/document-1'],
            [b.getPath() for b in self.catalog(
                portal_type='opengever.document.document')])

    def test_leaves_new_private_folder_untouched_if_old_one_doesnt_exist(self):
        self.login('hans.muster')
        create_members_folder(self.root)
        private_folder = self.root['hans.muster']

        dossier = create(Builder('private_dossier')
                         .within(private_folder)
                         .titled(u'Dossier in old private folder'))
        create(Builder('document')
               .within(dossier)
               .titled(u'Doc in old private folder'))

        self.login('manager')
        results = PrivateFoldersMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(
            [],
            results['private_folders']['moved'])

        # New folder should contain dossier
        self.assertItemsEqual(
            ['dossier-1'], self.root['hans.muster'].objectIds())

        # Old document should be in new location and properly reindexed
        self.assertItemsEqual(
            ['/plone/private/hans.muster/dossier-1/document-1'],
            [b.getPath() for b in self.catalog(
                portal_type='opengever.document.document')])

    def test_does_nothing_if_no_private_folders_exist(self):
        self.login('manager')
        results = PrivateFoldersMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(
            [],
            results['private_folders']['moved'])
