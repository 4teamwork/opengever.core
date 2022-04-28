from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from zope.component import queryMultiAdapter


class TestTrashListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='trash')
        return adapter.get_actions() if adapter else []

    def test_trash_actions_for_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'untrash_content']
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_trash_actions_for_closed_dossier(self):
        self.login(self.regular_user)
        self.assertEqual([], self.get_actions(self.expired_dossier))

    def test_trash_actions_for_inbox(self):
        self.login(self.secretariat_user)
        expected_actions = [u'untrash_content']
        self.assertEqual(expected_actions, self.get_actions(self.inbox))

    def test_remove_available_for_manager(self):
        self.login(self.manager)
        self.assertIn(u'remove', self.get_actions(self.dossier))
        self.assertIn(u'remove', self.get_actions(self.inbox))

    def test_trash_actions_for_private_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'untrash_content', u'delete']
        self.assertEqual(expected_actions, self.get_actions(self.private_dossier))

    def test_trash_actions_for_workspace_and_workspace_folder(self):
        self.login(self.workspace_member)
        expected_actions = [u'untrash_content', u'delete_workspace_content']
        self.assertEqual(expected_actions, self.get_actions(self.workspace))
        self.assertEqual(expected_actions, self.get_actions(self.workspace_folder))

    def test_untrash_content_not_available_if_context_is_trashed(self):
        self.login(self.workspace_member)
        ITrasher(self.workspace_folder).trash()
        self.assertNotIn(u'untrash_content', self.get_actions(self.workspace_folder))
