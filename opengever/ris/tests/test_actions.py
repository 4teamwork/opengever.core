from opengever.base.interfaces import IContextActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestRisProposalContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_ris_proposal_context_actions(self):
        self.activate_feature('ris')
        self.login(self.regular_user)
        expected_actions = [u'create_task_from_proposal']
        self.assertEqual(expected_actions, self.get_actions(self.ris_proposal))
