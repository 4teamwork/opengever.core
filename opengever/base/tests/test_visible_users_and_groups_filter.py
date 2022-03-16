from ftw.builder import Builder
from ftw.builder import create
from opengever.base.visible_users_and_groups_filter import VisibleUsersAndGroupsFilter
from opengever.ogds.models.group import Group
from opengever.testing import SolrIntegrationTestCase


class TestVisibleUsersAndGroupsFilterInGever(SolrIntegrationTestCase):

    def test_can_access_principal_is_always_possible(self):
        self.deactivate_feature('workspace')
        self.login(self.regular_user)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))


class TestVisibleUsersAndGroupsFilterInTeamraum(SolrIntegrationTestCase):

    features = ('workspace', )

    def test_can_access_principal_is_not_possible_without_permission(self):
        self.login(self.workspace_guest)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertFalse(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))

    def test_can_access_principal_is_always_possible_with_permission(self):
        self.login(self.workspace_admin)

        self.assertTrue(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())
        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal('example.user'))

    def test_can_access_principal_is_only_possible_for_whitelisted_principals(self):
        self.login(self.workspace_guest)

        self.assertFalse(VisibleUsersAndGroupsFilter().has_all_users_and_groups_permission())

        self.assertTrue(VisibleUsersAndGroupsFilter().can_access_principal(self.workspace_member.getId()))
        self.assertFalse(VisibleUsersAndGroupsFilter().can_access_principal(self.regular_user.getId()))

    def test_no_whitelisted_principals_if_not_in_any_workspace(self):
        self.login(self.regular_user)

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 0)
        self.assertItemsEqual(
            [self.regular_user.getId()], VisibleUsersAndGroupsFilter().get_whitelisted_principals(),
            "Only the current users should be whitelisted.")

    def test_all_members_of_a_workspace_should_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])

        # The regular user is now member of the project a workspace. Thus, the workspace creator should be
        # whitelisted, too.
        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 1)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_all_members_of_multiple_workspaces_should_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            workspace_project_b = create(Builder('workspace').titled(u'Project B').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.workspace_guest.getId(), ['WorkspaceGuest'])

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 2)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId(), self.workspace_guest.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_members_of_other_workspaces_should_not_be_whitelisted(self):
        self.login(self.regular_user)

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            workspace_project_b = create(Builder('workspace').titled(u'Project B').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])
            self.set_roles(workspace_project_b, self.workspace_guest.getId(), ['WorkspaceGuest'])

        self.assertEqual(len(self.portal.portal_catalog(portal_type='opengever.workspace.workspace')), 1)
        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

    def test_group_members_should_be_whitelisted(self):
        self.login(self.regular_user)
        group = Group.query.get('projekt_a')

        with self.login(self.workspace_admin):
            workspace_project_a = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
            self.set_roles(workspace_project_a, self.regular_user.getId(), ['WorkspaceMember'])

        self.assertItemsEqual(
            [self.regular_user.getId(), self.workspace_admin.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())

        with self.login(self.workspace_admin):
            self.set_roles(workspace_project_a, group.groupid, ['WorkspaceMember'])

        self.assertItemsEqual(
            [
                self.regular_user.getId(),
                self.workspace_admin.getId(),
                group.groupid,
                self.dossier_responsible.getId()],
            VisibleUsersAndGroupsFilter().get_whitelisted_principals())
