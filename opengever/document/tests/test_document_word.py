from opengever.testing import IntegrationTestCase


class TestDocumentProposal(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    def test_get_proposal_returns_None_for_regular_document(self):
        self.login(self.dossier_responsible)
        self.assertIsNone(self.document.get_proposal())

    def test_get_proposal_of_proposal_document_in_case_dossier(self):
        self.login(self.dossier_responsible)
        proposal = self.word_proposal
        self.assertEquals(proposal, proposal.get_proposal_document().get_proposal())

    def test_get_proposal_of_proposal_document_in_committee(self):
        self.login(self.committee_responsible)
        proposal = self.submitted_word_proposal
        self.assertEquals(proposal, proposal.get_proposal_document().get_proposal())
