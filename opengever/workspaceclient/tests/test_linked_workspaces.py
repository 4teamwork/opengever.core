from ftw.builder import Builder
from ftw.builder import create
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
import transaction


class TestLinkedWorkspaces(FunctionalWorkspaceClientTestCase):

    def test_list_linked_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)

            self.assertEqual([], manager.list())

            manager.storage.add(self.workspace.UID())

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list()])

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
                [workspace.get('@id') for workspace in manager.list()])

            self.grant('WorkspaceMember', on=unauthorized_workspace)
            transaction.commit()

            self.invalidate_cache()
            self.assertItemsEqual(
                [self.workspace.absolute_url(),
                 authorized_workspace.absolute_url(),
                 unauthorized_workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list()])

    def test_cache_list_stored_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            self.workspace.title = 'Old title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list()])

            self.workspace.title = 'New title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list()])

            self.invalidate_cache()
            self.assertEqual(['New title'],
                             [workspace.get('title') for workspace in manager.list()])

    def test_create_workspace_will_store_workspace_in_the_storage(self):
        with self.workspace_client_env() as client:
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual([], manager.list())

            with self.observe_children(self.workspace_root) as children:
                response = manager.create(title=u"My new w\xf6rkspace")
                transaction.commit()

            self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

            workspace = children['added'].pop()
            self.assertEqual([workspace.absolute_url()],
                             [ws.get('@id') for ws in manager.list()])
