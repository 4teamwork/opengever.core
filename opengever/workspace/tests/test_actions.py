from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from zope.component import queryMultiAdapter


class TestWorkspaceFolderListingActions(IntegrationTestCase):

    features = ('workspace', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='workspace_folders')
        return adapter.get_actions() if adapter else []

    def test_workspace_folder_actions_for_workspace_and_workspace_folder(self):
        self.login(self.workspace_member)
        expected_actions = [u'copy_items', u'move_items', u'zip_selected', u'trash_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))


class TestTodoContextActions(IntegrationTestCase):

    features = ('workspace', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_todo_context_actions(self):
        self.login(self.workspace_member)
        self.assertEqual([u'delete', u'edit', u'share_content'], self.get_actions(self.todo))

        self.login(self.workspace_guest)
        self.assertEqual([u'share_content'], self.get_actions(self.todo))

        with self.login(self.workspace_admin):
            self.workspace.hide_members_for_guests = True

        self.assertEqual([], self.get_actions(self.todo))


class TestWorkspaceMeetingContextActions(IntegrationTestCase):

    features = ('workspace', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_meeting_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'meeting_ical_download', u'meeting_minutes_pdf',
                            u'share_content', u'save_minutes_as_pdf']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_meeting))

        self.login(self.workspace_guest)
        self.assertEqual(
            [u'meeting_ical_download', u'meeting_minutes_pdf', u'share_content',
             u'save_minutes_as_pdf'],
            self.get_actions(self.workspace_meeting))

        with self.login(self.workspace_admin):
            self.workspace.hide_members_for_guests = True

        self.assertEqual(
            [u'meeting_ical_download', u'meeting_minutes_pdf',
             u'save_minutes_as_pdf'],
            self.get_actions(self.workspace_meeting))


class TestWorkspaceContextActions(IntegrationTestCase):

    features = ('workspace', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'share_content', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))

    def test_workspace_context_actions_for_guests(self):
        self.login(self.workspace_guest)
        self.assertEqual([u'share_content', 'zipexport'],
                         self.get_actions(self.workspace))

        with self.login(self.workspace_admin):
            self.workspace.hide_members_for_guests = True

        self.assertEqual([u'zipexport'], self.get_actions(self.workspace))

    def test_workspace_with_guest_restriction_context_actions_for_guests(self):
        self.login(self.workspace_guest)

        self.assertEqual([u'share_content', 'zipexport'],
                         self.get_actions(self.workspace))

        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.assertEqual([], self.get_actions(self.workspace))

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

    features = ('workspace', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_workspace_folder_context_actions(self):
        self.login(self.workspace_member)
        expected_actions = [u'edit', u'share_content', u'trash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_workspace_context_actions_for_guests(self):
        self.login(self.workspace_guest)
        self.assertEqual([u'share_content', 'zipexport'],
                         self.get_actions(self.workspace_folder))

        with self.login(self.workspace_admin):
            self.workspace.hide_members_for_guests = True

        self.assertEqual([u'zipexport'], self.get_actions(self.workspace_folder))

    def test_workspace_folder_context_actions_for_guests_in_workspace_with_guest_restriction(self):
        self.login(self.workspace_guest)
        self.assertEqual([u'share_content', 'zipexport'],
                         self.get_actions(self.workspace_folder))

        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.assertEqual([], self.get_actions(self.workspace_folder))

    def test_workspace_folder_context_actions_for_workspace_admins(self):
        self.login(self.workspace_admin)
        expected_actions = [u'edit', u'local_roles', u'share_content', u'trash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_context_action_for_trashed_workspace_folder(self):
        self.login(self.workspace_member)
        ITrasher(self.workspace_folder).trash()
        expected_actions = [u'delete_workspace_context', u'share_content', u'untrash_context', 'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))
