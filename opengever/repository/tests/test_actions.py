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
