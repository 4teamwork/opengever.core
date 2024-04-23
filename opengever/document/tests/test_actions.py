from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
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

    def test_document_actions_in_workspace_and_workspace_folder_for_member(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit_items', u'attach_documents', u'copy_items', u'move_items',
                            u'zip_selected', u'export_documents', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_document_actions_in_workspace_and_workspace_folder_for_guest(self):
        self.login(self.workspace_guest)
        expected_actions = [u'attach_documents', u'zip_selected', u'export_documents']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_document_actions_in_workspace_and_workspace_folder_with_guest_restriction(self):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True
        self.login(self.workspace_guest)
        expected_actions = []
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


class TestDocumentContextActions(IntegrationTestCase):

    features = ('bumblebee', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_context_actions_for_document_in_dossier(self):
        self.login(self.regular_user)
        expected_actions = [
            u'attach_to_email',
            u'checkout_document',
            u'copy_item',
            u'download_copy',
            u'edit',
            u'move_item',
            u'new_task_from_document',
            u'oc_direct_checkout',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
            u'trash_context',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.document))

    def test_context_actions_for_trashed_document_in_dossier(self):
        self.login(self.regular_user)
        ITrasher(self.document).trash()
        expected_actions = [
            u'oc_view',
            u'revive_bumblebee_preview',
            u'untrash_context',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.document))

    def test_context_actions_for_checked_out_document(self):
        self.login(self.regular_user)
        self.assertIn(u'copy_item', self.get_actions(self.document))
        queryMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        expected_actions = [
            u'attach_to_email',
            u'cancel_checkout',
            u'checkin_with_comment',
            u'checkin_without_comment',
            u'download_copy',
            u'edit',
            u'new_task_from_document',
            u'oc_direct_edit',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.document))

    def test_context_actions_for_document_in_inbox(self):
        self.login(self.secretariat_user)
        expected_actions = [
            u'attach_to_email',
            u'checkout_document',
            u'copy_item',
            u'create_forwarding',
            u'download_copy',
            u'edit',
            u'move_item',
            u'oc_direct_checkout',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
            u'trash_context',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.inbox_document))

    def test_context_actions_for_proposal_document(self):
        self.login(self.regular_user)
        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'new_task_from_document',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.proposaldocument))

    def test_context_actions_for_task_document(self):
        self.login(self.regular_user)
        expected_actions = [
            u'attach_to_email',
            u'checkout_document',
            u'copy_item',
            u'download_copy',
            u'edit',
            u'new_task_from_document',
            u'oc_direct_checkout',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
            u'trash_context',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.taskdocument))

    def test_context_actions_for_template_document(self):
        self.login(self.administrator)
        expected_actions = [
            u'checkout_document',
            u'copy_item',
            u'delete',
            u'download_copy',
            u'edit',
            u'move_item',
            u'oc_direct_checkout',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.normal_template))

    def test_context_actions_for_document_in_dossier_template(self):
        self.login(self.administrator)
        template = create(Builder('document')
                          .within(self.dossiertemplate)
                          .titled(u'Werkst\xe4tte')
                          .with_dummy_content())
        expected_actions = [
            u'checkout_document',
            u'copy_item',
            u'delete',
            u'download_copy',
            u'edit',
            u'move_item',
            u'oc_direct_checkout',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
        ]
        self.assertEqual(expected_actions, self.get_actions(template))

    def test_document_actions_in_workspace_with_guest(self):
        self.login(self.workspace_guest)

        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'move_item',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'save_document_as_pdf',
            u'share_content']

        self.assertEqual(expected_actions,
                         self.get_actions(self.workspace_document))

    def test_document_actions_in_workspace_with_guest_restriction(self):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.login(self.workspace_guest)
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        expected_actions_restricted_guest = [u'revive_bumblebee_preview']
        self.assertEqual(expected_actions_restricted_guest, self.get_actions(document))
