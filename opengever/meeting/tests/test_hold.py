from opengever.testing import IntegrationTestCase


class TestHoldMeeting(IntegrationTestCase):

    features = ('meeting',)

    def test_change_workflow_state(self):
        self.login(self.committee_responsible)

        self.meeting.model.hold()

        self.assertEquals('held', self.meeting.model.workflow_state)

    def test_generates_meeting_number(self):
        self.login(self.committee_responsible)

        self.meeting.model.hold()

        self.assertEquals(2, self.meeting.model.meeting_number)

    def test_generate_decision_numbers(self):
        self.login(self.committee_responsible)

        agenda_item_1 = self.schedule_proposal(
            self.meeting, self.submitted_word_proposal)
        agenda_item_2 = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        self.meeting.model.hold()

        self.assertEquals(2, agenda_item_1.decision_number)
        self.assertEquals(3, agenda_item_2.decision_number)
