from opengever.testing import IntegrationTestCase


class TestDocumentProposal(IntegrationTestCase):
    features = ('meeting',)

    def test_get_proposal_returns_None_for_regular_document(self):
        self.login(self.dossier_responsible)
        self.assertIsNone(self.document.get_proposal())

    def test_get_proposal_of_proposal_document_in_case_dossier(self):
        self.login(self.dossier_responsible)
        proposal = self.proposal
        self.assertEquals(proposal, proposal.get_proposal_document().get_proposal())

    def test_get_proposal_of_proposal_document_in_committee(self):
        self.login(self.committee_responsible)
        proposal = self.submitted_proposal
        self.assertEquals(proposal, proposal.get_proposal_document().get_proposal())

    def test_get_proposal_of_excerpt_document_in_committee(self):
        self.login(self.committee_responsible)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        with self.observe_children(self.meeting_dossier) as children:
            agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')

        excerpt_document, = children['added']
        self.assertEquals(self.submitted_proposal, excerpt_document.get_proposal())

    def test_get_proposal_of_excerpt_document_in_case_dossier(self):
        self.login(self.committee_responsible)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        with self.observe_children(self.meeting_dossier) as children:
            agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')

        meeting_dossier_excerpt, = children['added']
        with self.observe_children(self.dossier) as children:
            self.submitted_proposal.load_model().return_excerpt(
                meeting_dossier_excerpt)

        case_dossier_excerpt, = children['added']
        with self.login(self.dossier_responsible):
            self.assertEquals(self.proposal, case_dossier_excerpt.get_proposal())
