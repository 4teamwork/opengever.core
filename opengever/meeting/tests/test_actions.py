from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestProposalListingActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request),
                                    interface=IListingActions,
                                    name='proposals')
        return adapter.get_actions() if adapter else []

    def test_proposal_actions_for_reporoot_repofolder_and_dossier(self):
        self.login(self.regular_user)
        expected_actions = [u'export_proposals']
        self.assertEqual(expected_actions, self.get_actions(self.repository_root))
        self.assertEqual(expected_actions, self.get_actions(self.branch_repofolder))
        self.assertEqual(expected_actions, self.get_actions(self.dossier))
        self.assertEqual(expected_actions, self.get_actions(self.meeting_dossier))

    def test_proposal_actions_for_plone_site(self):
        self.login(self.regular_user)
        expected_actions = [u'export_proposals']
        self.assertEqual(expected_actions, self.get_actions(self.portal))


class TestProposalContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_proposal_context_actions(self):
        self.activate_feature('meeting')
        self.login(self.regular_user)
        expected_actions = [u'create_task_from_proposal', u'submit_additional_documents']
        self.assertEqual(expected_actions, self.get_actions(self.proposal))
