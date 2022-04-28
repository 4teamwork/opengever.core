from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
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
