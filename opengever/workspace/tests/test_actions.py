from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from zope.component import queryMultiAdapter


class TestWorkspaceFolderListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='workspace_folders')
        return adapter.get_actions() if adapter else []

    def test_workspace_folder_actions_for_workspace_and_workspace_folder(self):
        self.login(self.workspace_member)
        expected_actions = [u'copy_items', u'move_items', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))


class TestTodoContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_todo_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'share_content']
        self.assertEqual(expected_actions, self.get_actions(self.todo))


class TestWorkspaceMeetingContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_meeting_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'meeting_ical_download', u'meeting_minutes_pdf',
                            u'share_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_meeting))


class TestWorkspaceContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'share_content', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))

    def test_workspace_context_actions_for_workspace_admins(self):
        self.login(self.workspace_admin)
        expected_actions = [u'add_invitation', u'edit', u'local_roles', u'share_content', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))

    def test_delete_action_only_available_for_deactivated_workspaces(self):
        self.login(self.administrator)
        self.assertNotIn(u'delete_workspace', self.get_actions(self.workspace))
        self.set_workflow_state('opengever_workspace--STATUS--inactive', self.workspace)
        self.assertIn(u'delete_workspace', self.get_actions(self.workspace))

    def test_delete_not_available_for_linked_workspaces(self):
        self.login(self.administrator)
        self.workspace.external_reference = u'dossier-UID'
        self.set_workflow_state('opengever_workspace--STATUS--inactive', self.workspace)
        self.assertNotIn(u'delete_workspace', self.get_actions(self.workspace))


class TestWorkspaceFolderContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_folder_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'share_content', u'trash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_workspace_folder_context_actions_for_workspace_admins(self):
        self.login(self.workspace_admin)
        expected_actions = [u'edit', u'local_roles', u'share_content', u'trash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_context_action_for_trashed_workspace_folder(self):
        self.login(self.workspace_member)
        ITrasher(self.workspace_folder).trash()
        expected_actions = [u'delete_workspace_context', u'share_content', u'untrash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))
