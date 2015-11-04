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
            ('CommitteeGroupMember',),
            dict(self.committee.get_local_roles())['client1_users'])

    def test_update_roles_removes_old_role(self):
        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')

        local_roles = dict(self.committee.get_local_roles())
        self.assertNotIn('client1_users', local_roles)
        self.assertEqual(('CommitteeGroupMember',), local_roles['foo'])

    def test_update_roles_preserves_unmanaged_roles(self):
        self.committee.manage_addLocalRoles('foo', ['Contributor', 'Reader'])
        self.committee.manage_addLocalRoles('client1_users', ['Contributor'])

        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')
        local_roles = dict(self.committee.get_local_roles())
        self.assertItemsEqual(
            ['CommitteeGroupMember', 'Contributor', 'Reader'],
            local_roles['foo'])
        self.assertItemsEqual(
            ['Contributor'],
            local_roles['client1_users'])
