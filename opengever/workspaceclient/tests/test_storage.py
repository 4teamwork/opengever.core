from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from persistent.list import PersistentList


class TestLinkedWorkspacesStorage(FunctionalWorkspaceClientTestCase):

    def test_store_gets_initialized(self):
        storage = LinkedWorkspacesStorage(self.dossier)

        self.assertIsInstance(storage._storage, PersistentList)

    def test_initialization_is_idempotent(self):
        storage = LinkedWorkspacesStorage(self.dossier)
        storage._storage.append('uid')

        self.assertEqual(['uid'], storage._storage)

        # Multiple initializations shouldn't remove existing data
        storage = LinkedWorkspacesStorage(self.dossier)

        self.assertEqual(['uid'], storage._storage)

    def test_add_uid_to_store(self):
        storage = LinkedWorkspacesStorage(self.dossier)
        storage.add(self.workspace.UID())

        self.assertEqual([self.workspace.UID()], storage._storage)

    def test_list_stored_uids(self):
        storage = LinkedWorkspacesStorage(self.dossier)
        storage.add('UID-1')
        storage.add('UID-2')

        self.assertEqual(['UID-1', 'UID-2'], storage.list())
