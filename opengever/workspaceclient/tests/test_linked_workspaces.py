from ftw.builder import Builder
from ftw.builder import create
from opengever.workspaceclient.exceptions import WorkspaceNotFound
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
import transaction


class TestLinkedWorkspaces(FunctionalWorkspaceClientTestCase):

    def test_list_linked_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)

            self.assertEqual([], manager.list().get('items'))

            manager.storage.add(self.workspace.UID())

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

    def test_list_skips_workspaces_if_no_view_permission(self):
        unauthorized_workspace = create(Builder('workspace').within(self.workspace_root))
        self.grant('', on=unauthorized_workspace)

        authorized_workspace = create(Builder('workspace').within(self.workspace_root))
        self.grant('View', on=unauthorized_workspace)

        self.assertTrue(api.user.has_permission('View', obj=self.workspace))
        self.assertTrue(api.user.has_permission('View', obj=authorized_workspace))
        self.assertFalse(api.user.has_permission('View', obj=unauthorized_workspace))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            manager.storage.add(authorized_workspace.UID())
            manager.storage.add(unauthorized_workspace.UID())

            self.assertItemsEqual(
                [self.workspace.absolute_url(), authorized_workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

            self.grant('WorkspaceMember', on=unauthorized_workspace)
            transaction.commit()

            self.invalidate_cache()
            self.assertItemsEqual(
                [self.workspace.absolute_url(),
                 authorized_workspace.absolute_url(),
                 unauthorized_workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

    def test_cache_list_stored_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            self.workspace.title = 'Old title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

            self.workspace.title = 'New title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

            self.invalidate_cache()
            self.assertEqual(['New title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

    def test_create_workspace_will_store_workspace_in_the_storage(self):
        with self.workspace_client_env() as client:
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual([], manager.list().get('items'))

            with self.observe_children(self.workspace_root) as children:
                response = manager.create(title=u"My new w\xf6rkspace")
                transaction.commit()

            self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

            workspace = children['added'].pop()
            self.assertEqual([workspace.absolute_url()],
                             [ws.get('@id') for ws in manager.list().get('items')])

    def test_subdossiers_do_not_provided_linked_workspaces(self):
        subdossier = create(Builder('dossier').within(self.dossier))

        with self.workspace_client_env():
            self.assertTrue(getAdapter(self.dossier, ILinkedWorkspaces))

            with self.assertRaises(ComponentLookupError):
                getAdapter(subdossier, ILinkedWorkspaces)

    def test_copy_document_without_file_to_workspace(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                response = manager.copy_document_to_workspace(document, self.workspace.UID())
                transaction.commit()

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()

            self.assertEqual(workspace_document.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_document.title, document.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

    def test_copy_document_to_workspace_raises_error_if_workspace_is_not_linked_to_the_dossier(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)

            self.assertNotIn(self.workspace.UID(), manager.storage)
            with self.assertRaises(WorkspaceNotLinked):
                manager.copy_document_to_workspace(document, self.workspace.UID())

    def test_copy_document_to_workspace_raises_error_if_workspace_could_not_be_found(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add('removed-workspace-uid')

            with self.assertRaises(WorkspaceNotFound):
                manager.copy_document_to_workspace(document, 'removed-workspace-uid')
