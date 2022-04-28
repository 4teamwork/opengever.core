from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestDossierListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='dossiers')
        return adapter.get_actions() if adapter else []

    def test_dossier_actions_for_reporoot_and_repofolder(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'copy_items', u'move_items', u'export_dossiers',
                            u'pdf_dossierlisting']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))

    def test_dossier_actions_for_plone_site(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'copy_items', u'move_items', u'export_dossiers',
                            u'pdf_dossierlisting']
        self.assertEqual(expected_actions, self.get_actions(self.portal))

    def test_dossier_actions_for_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'copy_items', u'move_items', u'export_dossiers',
                            u'pdf_dossierlisting']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_create_disposition_available_for_archivist(self):
        self.login(self.archivist)
        self.assertIn(u'create_disposition', self.get_actions(self.repository_root))
        self.assertIn(u'create_disposition', self.get_actions(self.branch_repofolder))
        self.assertIn(u'create_disposition', self.get_actions(self.dossier))

    def test_create_disposition_available_for_records_manager(self):
        self.login(self.records_manager)
        self.assertIn(u'create_disposition', self.get_actions(self.repository_root))
        self.assertIn(u'create_disposition', self.get_actions(self.branch_repofolder))
        self.assertIn(u'create_disposition', self.get_actions(self.dossier))

    def test_dossier_actions_for_private_dossier_and_private_folder(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'export_dossiers', u'pdf_dossierlisting', u'delete']
        self.assertEqual(expected_actions, self.get_actions(self.private_dossier))
        self.assertEqual(expected_actions, self.get_actions(self.private_folder))
