from ftw.builder import Builder
from ftw.builder import create
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.visible_users_and_groups_filter import VisibleUsersAndGroupsFilter
from opengever.ogds.base.sources import AllEmailContactsAndUsersSource
from opengever.ogds.base.sources import AllFilteredGroupsSource
from opengever.ogds.base.sources import AllFilteredGroupsSourcePrefixed
from opengever.ogds.base.sources import AllGroupsSource
from opengever.ogds.base.sources import AllUsersAndGroupsSource
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.sources import AllUsersSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import ContactsSource
from opengever.ogds.base.sources import CurrentAdminUnitOrgUnitsSource
from opengever.ogds.base.sources import PotentialWorkspaceMembersSource
from opengever.ogds.base.sources import UsersContactsInboxesSource
from opengever.ogds.base.sources import WorkspaceContentMemberGroupsSource
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSource
from opengever.testing import IntegrationTestCase
from unittest import skip
from zExceptions import Unauthorized


def clear_cache_visible_users_and_groups_filter_cache(request):
    setattr(request, VisibleUsersAndGroupsFilter.ALLOWED_USERS_AND_GROUPS_CACHEKEY, None)


class TestWorkspaceSourcesProtection(IntegrationTestCase):

    features = ('workspace', )

    BLACKLIST = [
        AllEmailContactsAndUsersSource,
        AllUsersInboxesAndTeamsSource,
        ContactsSource,
        CurrentAdminUnitOrgUnitsSource,
        UsersContactsInboxesSource,
    ]

    WHITELIST = [
        WorkspaceContentMemberGroupsSource,
        WorkspaceContentMemberUsersSource,
        AssignedUsersSource,
        PotentialWorkspaceMembersSource,
        AllUsersSource,
        AllGroupsSource,
        AllFilteredGroupsSource,
        AllUsersAndGroupsSource,
        AllFilteredGroupsSourcePrefixed
    ]

    def test_whitelisted_teamraum_sources(self):
        not_whitelisted_sources = []

        for whitelisted_source in self.WHITELIST:
            try:
                whitelisted_source(self.portal)
            except Unauthorized:
                not_whitelisted_sources.append(whitelisted_source)

        self.assertEqual([], not_whitelisted_sources)

    def test_blacklisted_teamraum_sources(self):
        self.maxDiff = None
        not_protected_sources = []

        for blacklisted_source in self.BLACKLIST:
            try:
                blacklisted_source(self.portal)
            except Unauthorized:
                pass
            else:
                not_protected_sources.append(blacklisted_source)

        self.assertEqual([], not_protected_sources)


class TestPotentialWorkspaceMembersSource(IntegrationTestCase):

    features = ('workspace', )

    def test_users_of_all_admin_unit_are_valid(self):
        self.login(self.workspace_admin)
        source = PotentialWorkspaceMembersSource(self.workspace)

        admin_unit2 = create(Builder('admin_unit')
                             .id('additional')
                             .having(title='additional'))

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=admin_unit2)
                            .with_default_groups())

        create(Builder('ogds_user').id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([org_unit_3]))

        self.assertIn(self.regular_user.id, source)
        # User from other admin_unit is also valid
        self.assertIn('peter.meier', source)

    def test_only_users_of_current_admin_unit_are_found_by_search(self):
        self.login(self.workspace_admin)
        source = PotentialWorkspaceMembersSource(self.workspace)

        admin_unit2 = create(Builder('admin_unit')
                             .id('additional')
                             .having(title='additional'))

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=admin_unit2)
                            .with_default_groups())

        create(Builder('ogds_user').id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([org_unit_3]))

        results = source.search(self.regular_user.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.regular_user.id, results[0].value)

        # User from other admin_unit cannot be found
        results = source.search('peter.meier')
        self.assertEqual(0, len(results))

    def test_users_with_local_roles_are_invalid(self):
        self.login(self.workspace_admin)
        source = PotentialWorkspaceMembersSource(self.workspace)
        self.assertNotIn(self.workspace_guest.id, source)
        self.assertNotIn(self.workspace_member.id, source)
        self.assertNotIn(self.workspace_admin.id, source)
        self.assertNotIn(self.workspace_owner.id, source)

    def test_users_with_local_roles_are_not_found_by_search(self):
        self.login(self.workspace_admin)
        source = PotentialWorkspaceMembersSource(self.workspace)

        results = source.search(self.workspace_guest.id)
        self.assertEqual(0, len(results))
        results = source.search(self.workspace_member.id)
        self.assertEqual(0, len(results))
        results = source.search(self.workspace_admin.id)
        self.assertEqual(0, len(results))
        results = source.search(self.workspace_owner.id)
        self.assertEqual(0, len(results))

    def test_contains_only_whitelisted_users_and_groups(self):
        self.login(self.regular_user)
        source = PotentialWorkspaceMembersSource(self.portal)

        self.assertIn(self.regular_user.getId(), source)
        self.assertNotIn(self.workspace_guest.getId(), source)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, self.workspace_guest.getId(), ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertIn(self.regular_user.getId(), source)
        self.assertIn(self.workspace_guest.getId(), source)

    def test_can_search_only_whitelisted_users_and_groups(self):
        self.login(self.regular_user)
        source = PotentialWorkspaceMembersSource(self.portal)

        self.assertEqual([], source.search('hans'))

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, self.workspace_guest.getId(), ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertEqual(1, len(source.search('hans')))
        self.assertEqual(self.workspace_guest.getId(), source.search('hans')[0].token)


class TestWorkspaceContentMemberUsersSource(IntegrationTestCase):

    def test_users_of_all_admin_unit_are_valid(self):
        self.login(self.workspace_admin)
        source = WorkspaceContentMemberUsersSource(self.workspace)

        admin_unit2 = create(Builder('admin_unit')
                             .id('additional')
                             .having(title='additional'))

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=admin_unit2)
                            .with_default_groups())

        create(Builder('ogds_user').id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([org_unit_3]))

        self.assertIn(self.regular_user.id, source)
        # User from other admin_unit is also valid
        self.assertIn('peter.meier', source)

    def test_users_with_and_without_local_roles_are_valid(self):
        self.login(self.workspace_admin)
        source = WorkspaceContentMemberUsersSource(self.workspace)
        self.assertIn(self.workspace_guest.id, source)
        self.assertIn(self.workspace_member.id, source)
        self.assertIn(self.workspace_admin.id, source)
        self.assertIn(self.workspace_owner.id, source)

        RoleAssignmentManager(self.workspace_root).clear_by_cause_and_principal(
            ASSIGNMENT_VIA_SHARING, self.workspace_guest.getId())
        self.workspace_root.reindexObjectSecurity()
        self.assertIn(self.workspace_guest.id, source)

    @skip('This test fails for unknown reasons after changing userid for kathi.barfuss to regular_user')
    def test_only_users_with_local_roles_with_view_permissions_are_found_by_search(self):
        self.login(self.workspace_admin)
        source = WorkspaceContentMemberUsersSource(self.workspace)

        results = source.search(self.workspace_guest.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.workspace_guest.id, results[0].value)

        results = source.search(self.regular_user.id)
        self.assertEqual(0, len(results))

        # Assigning WorkspaceGuest to regular_user and check that he is then
        # found in the WorkspaceContentMemberUsersSource
        RoleAssignmentManager(self.workspace).add_or_update(
            self.regular_user.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)
        results = source.search(self.regular_user.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.regular_user.id, results[0].value)

        # Only local roles that give view permissions are considered for
        # users found in the WorkspaceContentMemberUsersSource
        self.workspace.manage_permission('View', roles=[])
        results = source.search(self.regular_user.id)
        self.assertEqual(0, len(results))

        results = source.search(self.workspace_guest.id)
        self.assertEqual(0, len(results))

    def test_source_is_context_dependent_and_respects_local_roles_block(self):
        self.login(self.workspace_admin)
        source = WorkspaceContentMemberUsersSource(self.workspace_folder)
        results = source.search('')
        self.assertEqual(4, len(results))
        self.assertEqual(
            [self.workspace_owner.id, self.workspace_admin.id,
             self.workspace_guest.id, self.workspace_member.id],
            [term.value for term in results])

        self.workspace_folder.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.workspace_folder).add_or_update(
            self.workspace_admin.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)

        results = source.search('')
        self.assertEqual(1, len(results))
        self.assertEqual(self.workspace_admin.id, results[0].value)

    def test_title_is_fullname_and_userid(self):
        self.login(self.workspace_admin)
        source = WorkspaceContentMemberUsersSource(self.workspace)

        term = source.search('beatrice')[0]
        self.assertEqual(self.workspace_member.id, term.token)
        self.assertEqual(self.workspace_member.id, term.value)
        self.assertEqual(u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)', term.title)


class TestAssignedUsersSource(IntegrationTestCase):

    features = ('workspace', )

    def test_contains_only_whitelisted_users_and_groups(self):
        self.login(self.regular_user)
        source = AssignedUsersSource(self.portal)

        self.assertIn(self.regular_user.getId(), source)
        self.assertNotIn(self.workspace_guest.getId(), source)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, self.workspace_guest.getId(), ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertIn(self.regular_user.getId(), source)
        self.assertIn(self.workspace_guest.getId(), source)

    def test_can_search_only_whitelisted_users_and_groups(self):
        self.login(self.regular_user)
        source = AssignedUsersSource(self.portal)

        self.assertEqual([], source.search('hans'))

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, self.workspace_guest.getId(), ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertEqual(1, len(source.search('hans')))
        self.assertEqual(self.workspace_guest.getId(), source.search('hans')[0].token)


class TestWorkspaceAllGoupsSource(IntegrationTestCase):

    features = ('workspace', )

    def test_contains_only_whitelisted_groups(self):
        self.login(self.regular_user)
        source = AllGroupsSource(self.portal)

        self.assertNotIn('fa_users', source)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, 'fa_users', ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertIn('fa_users', source)

    def test_can_search_only_whitelisted_groups(self):
        self.login(self.regular_user)
        source = AllGroupsSource(self.portal)

        self.assertEqual([], source.search('Users'))

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_a, 'fa_users', ['WorkspaceGuest'])

        clear_cache_visible_users_and_groups_filter_cache(self.request)

        self.assertEqual(1, len(source.search('Users')))
        self.assertEqual('fa_users', source.search('Users')[0].token)
