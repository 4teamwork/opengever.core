from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.dossier.resolve import LockingResolveManager
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zope.component import queryMultiAdapter
import transaction


class TestDossierListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='dossiers')
        return adapter.get_actions() if adapter else []

    def test_dossier_actions_for_reporoot_and_repofolder(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'change_items_state', u'copy_items',
                            u'move_items', u'export_dossiers', u'export_dossiers_with_subdossiers',
                            u'pdf_dossierlisting', u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))

    def test_dossier_actions_for_plone_site(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'change_items_state', u'copy_items',
                            u'move_items', u'export_dossiers', u'export_dossiers_with_subdossiers',
                            u'pdf_dossierlisting', u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.portal))

    def test_dossier_actions_for_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'edit_items', u'change_items_state', u'copy_items',
                            u'move_items', u'export_dossiers', u'export_dossiers_with_subdossiers',
                            u'pdf_dossierlisting', u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_create_disposition_available_for_archivist(self):
        self.login(self.archivist)
        self.assertIn(u'create_disposition', self.get_actions(self.repository_root))
        self.assertIn(u'create_disposition', self.get_actions(self.branch_repofolder))
        self.assertNotIn(u'create_disposition', self.get_actions(self.dossier))

    def test_create_disposition_available_for_records_manager(self):
        self.login(self.records_manager)
        self.assertIn(u'create_disposition', self.get_actions(self.repository_root))
        self.assertIn(u'create_disposition', self.get_actions(self.branch_repofolder))
        self.assertNotIn(u'create_disposition', self.get_actions(self.dossier))

    def test_dossier_actions_for_private_dossier_and_private_folder(self):
        self.login(self.regular_user)
        expected_actions = [
            u'edit_items', u'change_items_state', u'export_dossiers',
            u'pdf_dossierlisting', u'delete', u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.private_dossier))
        self.assertEqual(expected_actions, self.get_actions(self.private_folder))


class TestWorkspaceClientDossierListingActions(FunctionalWorkspaceClientTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='dossiers')
        return adapter.get_actions() if adapter else []

    def test_copy_dossier_to_workspace_action_available_in_open_dossier_with_linked_workspaces(self):
        with self.workspace_client_env():
            self.assertNotIn(u'copy_dossier_to_workspace', self.get_actions(self.dossier))
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()
            self.assertIn(u'copy_dossier_to_workspace', self.get_actions(self.dossier))

            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-deactivate')

            self.assertNotIn(u'copy_dossier_to_workspace', self.get_actions(self.dossier))


class TestDossierTemplateListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='dossiertemplates')
        return adapter.get_actions() if adapter else []

    def test_dossiertemplate_actions_for_templatefolder_and_dossiertemplate(self):
        self.login(self.regular_user)
        self.assertEqual([u'move_items'], self.get_actions(self.templates))
        self.assertEqual([u'move_items'], self.get_actions(self.dossiertemplate))

        self.login(self.administrator)
        expected_actions = [u'move_items', u'delete']
        self.assertEqual(expected_actions, self.get_actions(self.templates))
        self.assertEqual(expected_actions, self.get_actions(self.dossiertemplate))


class TestDossierContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_dossier_context_actions(self):
        self.login(self.regular_user)
        expected_actions = [
            u'document_with_template',
            u'edit', u'export_pdf',
            u'pdf_dossierdetails', u'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))

    def test_dossier_context_actions_with_manager(self):
        self.login(self.manager)
        expected_actions = [
            u'document_with_template',
            u'edit', u'export_pdf', u'local_roles',
            u'pdf_dossierdetails', u'protect_dossier', u'zipexport',
            u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))

    def test_dossier_context_actions_with_limited_admin(self):
        self.login(self.limited_admin)
        expected_actions = [
            u'document_with_template',
            u'edit', u'export_pdf',
            u'pdf_dossierdetails', u'zipexport',
            u'transfer_dossier_responsible']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))

    def test_document_from_docugate_available_if_feature_enabled(self):
        self.login(self.regular_user)
        self.assertNotIn(u'document_from_docugate', self.get_actions(self.dossier))
        self.activate_feature('docugate')
        self.assertIn(u'document_from_docugate', self.get_actions(self.dossier))

    def test_protect_dossier_available_for_dossier_manager(self):
        self.login(self.dossier_manager)
        self.assertIn(u'protect_dossier', self.get_actions(self.dossier))

    def test_document_with_oneoffixx_template_available_if_feature_enabled(self):
        self.login(self.regular_user)
        self.assertNotIn(u'document_with_oneoffixx_template',
                         self.get_actions(self.dossier))
        self.activate_feature('oneoffixx')
        self.assertIn(u'document_with_oneoffixx_template', self.get_actions(self.dossier))

    def test_add_dossier_transfer_action(self):
        self.login(self.secretariat_user)
        LockingResolveManager(self.resolvable_dossier).resolve()

        self.login(self.regular_user)

        # Only available when feature is activated
        self.assertNotIn(u'add_dossier_transfer', self.get_actions(self.dossier))
        self.assertNotIn(u'add_dossier_transfer', self.get_actions(self.resolvable_dossier))

        self.activate_feature('dossier-transfers')

        # Only available for resolved dossiers
        self.assertNotIn(u'add_dossier_transfer', self.get_actions(self.dossier))
        self.assertIn(u'add_dossier_transfer', self.get_actions(self.resolvable_dossier))

        # Only available if user has view permission
        # Can't really test this here, because traversal and several other
        # things already don't work if the user doesn't have 'View' on the obj.


class TestWorkspaceClientDossierContextActions(FunctionalWorkspaceClientTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def link_workspace(self, obj):
        manager = ILinkedWorkspaces(obj)
        manager.storage.add(self.workspace.UID())
        transaction.commit()

    def test_context_actions_for_dossier_with_linked_workspace(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            expected_actions = [u'copy_documents_from_workspace', u'copy_documents_to_workspace',
                                u'create_linked_workspace', u'document_with_template', u'edit',
                                u'export_pdf', u'link_to_workspace', u'list_workspaces',
                                u'pdf_dossierdetails', u'unlink_workspace', u'zipexport']

            self.assertEqual(expected_actions, self.get_actions(self.dossier))

    def test_context_actions_for_subdossier(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            subdossier = create(Builder('dossier').within(self.dossier))
            expected_actions = [u'copy_documents_to_workspace', u'delete', u'document_with_template', u'edit',
                                u'export_pdf', u'list_workspaces', u'pdf_dossierdetails',
                                u'zipexport']

            self.assertEqual(expected_actions, self.get_actions(subdossier))

    def test_copy_documents_and_unlink_not_available_in_dossier_without_linked_workspaces(self):
        with self.workspace_client_env():
            actions = self.get_actions(self.dossier)
            self.assertNotIn(u'copy_documents_from_workspace', actions)
            self.assertNotIn(u'copy_documents_to_workspace',  actions)
            self.assertNotIn(u'unlink_workspace',  actions)

    def test_link_to_workspace_action_only_available_if_linking_activated(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            self.assertIn(u'link_to_workspace', self.get_actions(self.dossier))
            self.enable_linking(False)
            self.assertNotIn(u'link_to_workspace', self.get_actions(self.dossier))

    def test_list_workspaces_only_available_if_user_has_permission_to_use_workspace_client(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)

            self.assertIn(u'list_workspaces', self.get_actions(self.dossier))
            roles = api.user.get_roles()
            roles.remove('WorkspaceClientUser')
            self.grant(*roles)
            self.assertNotIn(u'list_workspaces', self.get_actions(self.dossier))

    def test_list_workspaces_only_available_if_workspace_client_feature_avtivated(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            self.assertIn(u'list_workspaces', self.get_actions(self.dossier))
            self.enable_feature(False)
            self.assertNotIn(u'list_workspaces', self.get_actions(self.dossier))

    def test_context_actions_for_closed_dossier(self):
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-deactivate')
            transaction.commit()
            expected_actions = [
                u'export_pdf', u'list_workspaces', u'pdf_dossierdetails',
                u'unlink_workspace', u'zipexport',
            ]
            self.assertEqual(expected_actions, self.get_actions(self.dossier))


class TestTemplateContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_template_folder_context_actions(self):
        self.login(self.administrator)
        expected_actions = [u'delete', u'edit', u'local_roles']
        self.assertEqual(expected_actions, self.get_actions(self.templates))

    def test_dossier_template_context_actions(self):
        self.login(self.administrator)
        expected_actions = [u'delete', u'edit', u'local_roles', u'move_item']
        self.assertEqual(expected_actions, self.get_actions(self.dossiertemplate))
