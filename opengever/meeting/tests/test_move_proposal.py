from ftw.testbrowser import browsing
from opengever.meeting.exceptions import ProposalMovedOutsideOfMainDossierError
from opengever.testing import IntegrationTestCase
from plone import api


class TestMoveProposal(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_a_proposal_can_be_moved_inside_of_its_main_dossier(self, browser):
        self.login(self.dossier_manager)
        proposal = self.proposal

        self.assertIn(proposal, self.dossier.objectValues())
        api.content.move(proposal, self.subdossier)
        self.assertIn(proposal, self.subdossier.objectValues())

    @browsing
    def test_it_is_not_allowed_to_move_a_proposal_outside_of_its_main_dossier(self, browser):
        self.login(self.dossier_manager)

        with self.assertRaises(ProposalMovedOutsideOfMainDossierError):
            api.content.move(self.proposal, self.resolvable_dossier)
