from opengever.testing import IntegrationTestCase


class TestCommitteeTraversal(IntegrationTestCase):
    features = ('meeting',)

    def test_can_only_access_contained_meetings(self):
        self.login(self.meeting_user)
        self.assertEquals(self.meeting.model.committee, self.committee.load_model())
        meeting_path_segment = 'meeting-{}'.format(self.meeting.model.meeting_id)
        self.assertEquals(self.meeting.model,
                          self.committee.get(meeting_path_segment).model)
        self.assertIsNone(self.empty_committee.get(meeting_path_segment))

    def test_can_only_access_contained_memberships(self):
        self.login(self.meeting_user)
        membership = self.committee.load_model().memberships[0]
        membership_path_segment = 'membership-{}'.format(membership.membership_id)
        self.assertEquals(membership, self.committee.get(membership_path_segment).model)
        self.assertIsNone(self.empty_committee.get(membership_path_segment))
