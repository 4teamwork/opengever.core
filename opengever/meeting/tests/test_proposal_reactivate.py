from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase
from plone import api


class TestProposalReactivate(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_proposal_can_be_reactivated(self, browser):
        self.login(self.dossier_responsible, browser)
        api.content.transition(self.draft_proposal, 'proposal-transition-cancel')

        self.assert_workflow_state('proposal-state-cancelled', self.draft_proposal)
        self.assertEqual(Proposal.STATE_CANCELLED, self.draft_proposal.get_state())

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-reactivate")
        browser.click_on("Confirm")

        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Review state changed successfully.')
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
