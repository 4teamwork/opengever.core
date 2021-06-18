from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IDeleter
from zExceptions import Forbidden


class TestDeleter(IntegrationTestCase):

    def test_may_not_delete_document_outside_workspace_root(self):
        self.login(self.manager)
        ITrasher(self.document).trash()
        deleter = IDeleter(self.document)
        with self.assertRaises(Forbidden):
            deleter.verify_may_delete()

    def test_document_may_only_be_delete_when_trashed(self):
        self.login(self.manager)
        deleter = IDeleter(self.workspace_document)
        with self.assertRaises(Forbidden):
            deleter.verify_may_delete()

        ITrasher(self.workspace_document).trash()
        deleter.verify_may_delete()

    def test_folder_may_only_be_deleted_when_trashed(self):
        self.login(self.manager)
        deleter = IDeleter(self.workspace_folder)
        with self.assertRaises(Forbidden):
            deleter.verify_may_delete()

        ITrasher(self.workspace_folder).trash()
        deleter.verify_may_delete()
