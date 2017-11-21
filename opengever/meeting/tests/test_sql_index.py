from opengever.testing import IntegrationTestCase


class TestSubmittedProposal(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    def test_sql_index_proposal_title_is_updated(self):
        # an agenda item is needed for this test
        self.login(self.committee_responsible)
        self.meeting.model.schedule_proposal(self.proposal.load_model())
        agenda_item = self.meeting.model.agenda_items[0]
        self.assertEquals(agenda_item.get_title(), agenda_item.proposal.submitted_title)

        agenda_item.set_title('New agenda item title')

        self.assertEquals('New agenda item title', agenda_item.get_title())
        self.assertEquals('New agenda item title', agenda_item.proposal.submitted_title)
