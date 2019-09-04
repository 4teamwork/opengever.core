from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase


class TestProposalCancel(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_proposal_can_be_cancelled(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-cancel")
        browser.click_on("Confirm")

        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Review state changed successfully.')

        self.assertEqual(Proposal.STATE_CANCELLED, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-cancelled', self.draft_proposal)
