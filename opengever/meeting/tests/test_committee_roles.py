from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.committeeroles import CommitteeRoles
from opengever.testing import FunctionalTestCase


class TestCommitteeTabs(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeTabs, self).setUp()

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container))

    def test_committee_roles_initialized(self):
        self.assertEqual(
            ('Contributor', 'Editor', 'Reader'),
            dict(self.committee.get_local_roles())['client1_users'])

    def test_update_roles_removes_old_role(self):
        CommitteeRoles('foo', previous_group_id='client1_users').update(
            self.committee)

        local_roles = dict(self.committee.get_local_roles())
        self.assertNotIn('client1_users', local_roles)
        self.assertEqual(
            ('Contributor', 'Editor', 'Reader'),
            local_roles['foo'])
