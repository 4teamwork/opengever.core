from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.committee import get_group_vocabulary
from opengever.meeting.committeeroles import CommitteeRoles
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase


class TestCommitteeTabs(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeTabs, self).setUp()

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container))

    def test_committee_roles_initialized(self):
        self.assertEqual(
            ('CommitteeResponsible', ),
            dict(self.committee.get_local_roles())['client1_users'])

    def test_update_roles_removes_old_role(self):
        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')

        local_roles = dict(self.committee.get_local_roles())
        self.assertNotIn('client1_users', local_roles)
        self.assertEqual(('CommitteeResponsible',),
                         local_roles['foo'])

    def test_update_roles_preserves_unmanaged_roles(self):
        self.committee.manage_addLocalRoles('foo',
            ['Contributor', 'Administrator'])
        self.committee.manage_addLocalRoles(
            'client1_users', ['Contributor'])

        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')
        local_roles = dict(self.committee.get_local_roles())
        self.assertItemsEqual(
            ['Administrator', 'CommitteeResponsible', 'Contributor'],
            local_roles['foo'])
        self.assertItemsEqual(
            ['Contributor'],
            local_roles['client1_users'])

    def test_principal_of_managed_roles_is_a_bytestring(self):
        for principal, roles in self.committee.get_local_roles():
            self.assertTrue(isinstance(principal, str), 'Not a byte string')


class TestCommitteeGroupsVocabulary(IntegrationTestCase):

    def test_return_all_groups(self):
        self.login(self.committee_responsible)

        self.assertItemsEqual(
            [u'fa_users',
             u'fa_inbox_users',
             u'projekt_a',
             u'projekt_b',
             u'committee_rpk_group',
             u'committee_ver_group'],
            [term.value for term in
             get_group_vocabulary(self.committee_container)])
