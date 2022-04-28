from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from zope.component import queryMultiAdapter
import transaction


class TestDocumentListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='documents')
        return adapter.get_actions() if adapter else []

    def test_document_actions_for_reporoot_and_repofolder(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'zip_selected', u'export_documents']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))

    def test_document_actions_for_open_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'create_task', u'zip_selected', u'export_documents', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_document_actions_for_closed_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'attach_documents', u'copy_items', u'zip_selected',
                            u'export_documents']
        self.assertEqual(expected_actions, self.get_actions(self.expired_dossier))

    def test_document_actions_for_dossier_with_meeting_feature(self):
        self.login(self.regular_user)
        self.activate_feature('meeting')
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'create_task', u'create_proposal', u'zip_selected',
                            u'export_documents', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_document_actions_for_private_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'zip_selected', u'export_documents', u'trash_content', u'delete']
        self.assertEqual(expected_actions, self.get_actions(self.private_dossier))

    def test_document_actions_for_private_folder(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'zip_selected', u'export_documents', u'delete']
        self.assertEqual(expected_actions, self.get_actions(self.private_folder))

    def test_document_actions_for_inbox(self):
        self.login(self.secretariat_user)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items',
                            u'move_items', u'create_forwarding', u'zip_selected',
                            u'export_documents', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.inbox))

    def test_document_actions_for_template_folder_and_dossier_template(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'copy_items', u'move_items', u'zip_selected',
                            u'export_documents']
        self.assertEqual(expected_actions, self.get_actions(self.templates))
        self.assertEqual(expected_actions, self.get_actions(self.dossiertemplate))

    def test_delete_action_available_for_admins_in_template_area(self):
        self.login(self.administrator)
        self.assertIn(u'delete', self.get_actions(self.templates))
        self.assertIn(u'delete', self.get_actions(self.dossiertemplate))

    def test_document_actions_for_workspace_and_workspace_folder(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'zip_selected', u'export_documents', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))


class TestWorkspaceClientDocumentListingActions(FunctionalWorkspaceClientTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='documents')
        return adapter.get_actions() if adapter else []

    def test_copy_documents_to_workspace_action_available_in_dossier_with_linked_workspaces(self):

        with self.workspace_client_env():
            self.assertNotIn(u'copy_documents_to_workspace', self.get_actions(self.dossier))
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()
            self.assertIn(u'copy_documents_to_workspace', self.get_actions(self.dossier))
