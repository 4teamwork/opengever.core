from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.committee import get_group_vocabulary
from opengever.meeting.committeeroles import CommitteeRoles
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import setRoles


class TestCommitteeTabs(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeTabs, self).setUp()

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container))

    def test_committee_roles_initialized(self):
        self.assertEqual(
            ('CommitteeGroupMember', 'Editor'),
            dict(self.committee.get_local_roles())['client1_users'])

    def test_update_roles_removes_old_role(self):
        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')

        local_roles = dict(self.committee.get_local_roles())
        self.assertNotIn('client1_users', local_roles)
        self.assertEqual(('CommitteeGroupMember', 'Editor'),
                         local_roles['foo'])

    def test_update_roles_preserves_unmanaged_roles(self):
        self.committee.manage_addLocalRoles('foo', ['Contributor', 'Reader'])
        self.committee.manage_addLocalRoles('client1_users', ['Contributor'])

        CommitteeRoles(self.committee).update(
            'foo', previous_principal='client1_users')
        local_roles = dict(self.committee.get_local_roles())
        self.assertItemsEqual(
            ['CommitteeGroupMember', 'Contributor', 'Editor', 'Reader'],
            local_roles['foo'])
        self.assertItemsEqual(
            ['Contributor'],
            local_roles['client1_users'])

    def test_principal_of_managed_roles_is_a_bytestring(self):
        for principal, roles in self.committee.get_local_roles():
            self.assertTrue(isinstance(principal, str), 'Not a byte string')


class TestCommitteeGroupsVocabulary(FunctionalTestCase):

    def test_return_empty_vocabulary_if_user_is_not_assigned_to_any_group(self):
        container = create(Builder('committee_container'))

        create(Builder('user').with_userid('hugo.boss'))
        create(Builder('ogds_user').id('hugo.boss'))

        login(self.layer['portal'], 'hugo.boss')

        self.assertEqual(
            [],
            [term for term in get_group_vocabulary(container)])

    def test_return_only_groups_where_the_user_is_assigned(self):
        container = create(Builder('committee_container'))

        create(Builder('user').with_userid('hugo.boss'))
        ogds_user = create(Builder('ogds_user').id('hugo.boss'))

        create(Builder('ogds_group').id('foo').having(users=[ogds_user, ]))
        create(Builder('ogds_group').id('bar'))

        login(self.layer['portal'], 'hugo.boss')

        self.assertEqual(
            [u'foo'],
            [term.value for term in get_group_vocabulary(container)])

    def test_return_all_groups_if_the_user_has_manager_role(self):
        container = create(Builder('committee_container'))

        create(Builder('user').with_userid('hugo.boss'))
        ogds_user = create(Builder('ogds_user').id('hugo.boss'))

        create(Builder('ogds_group').id('foo').having(users=[ogds_user, ]))
        create(Builder('ogds_group').id('bar'))

        setRoles(self.layer['portal'], 'hugo.boss', ['Manager'])

        login(self.layer['portal'], 'hugo.boss')

        self.assertEqual(
            [u'client1_users', u'client1_inbox_users', u'foo', u'bar'],
            [term.value for term in get_group_vocabulary(container)])
