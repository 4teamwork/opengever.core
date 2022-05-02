from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IContextActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestRepositoryRootContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_repository_root_context_actions(self):
        self.login(self.regular_user)
        self.assertEqual([], self.get_actions(self.repository_root))
        self.login(self.administrator)
        expected_actions = [u'download_excel', u'edit', u'local_roles', u'prefix_manager']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))


class TestRepositoryFolderContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_repository_folder_context_actions(self):
        self.login(self.regular_user)
        self.assertEqual([], self.get_actions(self.branch_repofolder))
        self.login(self.administrator)
        expected_actions = [u'edit', u'local_roles', u'prefix_manager']
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))

    def test_delete_action_only_available_for_empty_repo_folders(self):
        self.login(self.administrator)
        self.assertIn(u'delete_repository', self.get_actions(self.empty_repofolder))
        create(Builder('dossier').within(self.empty_repofolder))
        self.assertNotIn(u'delete_repository', self.get_actions(self.empty_repofolder))

    def test_dossier_with_template_only_available_if_repo_folder_is_leafnode(self):
        self.activate_feature('dossiertemplate')
        self.login(self.regular_user)
        self.assertIn(u'dossier_with_template', self.get_actions(self.empty_repofolder))
        create(Builder('repository').within(self.empty_repofolder))
        self.assertNotIn(u'dossier_with_template', self.get_actions(self.empty_repofolder))
