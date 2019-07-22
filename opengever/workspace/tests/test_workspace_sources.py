from ftw.builder import Builder
from ftw.builder import create
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.ogds.base.sources import PotentialWorkspaceMembersSource
from opengever.ogds.base.sources import ActualWorkspaceMembersSource
from opengever.testing import IntegrationTestCase


class TestPotentialWorkspaceMembersSource(IntegrationTestCase):

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

    def test_users_with_local_roles_are_valid(self):
        self.login(self.workspace_admin)
        source = PotentialWorkspaceMembersSource(self.workspace)
        self.assertIn(self.workspace_guest.id, source)
        self.assertIn(self.workspace_member.id, source)
        self.assertIn(self.workspace_admin.id, source)
        self.assertIn(self.workspace_owner.id, source)

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


class TestActualWorkspaceMembersSource(IntegrationTestCase):

    def test_users_of_all_admin_unit_are_valid(self):
        self.login(self.workspace_admin)
        source = ActualWorkspaceMembersSource(self.workspace)

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
        source = ActualWorkspaceMembersSource(self.workspace)

        admin_unit2 = create(Builder('admin_unit')
                             .id('additional')
                             .having(title='additional'))

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=admin_unit2)
                            .with_default_groups())

        peter = create(Builder('ogds_user').id('peter.meier')
                       .having(firstname='Peter', lastname='Meier')
                       .assign_to_org_units([org_unit_3]))

        RoleAssignmentManager(self.workspace).add_or_update(
            self.regular_user.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)
        RoleAssignmentManager(self.workspace).add_or_update(
            peter.userid, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)

        results = source.search(self.regular_user.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.regular_user.id, results[0].value)

        # User from other admin_unit cannot be found
        results = source.search('peter.meier')
        self.assertEqual(0, len(results))

    def test_users_with_and_without_local_roles_are_valid(self):
        self.login(self.workspace_admin)
        source = ActualWorkspaceMembersSource(self.workspace)
        self.assertIn(self.workspace_guest.id, source)
        self.assertIn(self.workspace_member.id, source)
        self.assertIn(self.workspace_admin.id, source)
        self.assertIn(self.workspace_owner.id, source)

        RoleAssignmentManager(self.workspace_root).clear_by_cause_and_principal(
            ASSIGNMENT_VIA_SHARING, self.workspace_guest.getId())
        self.workspace_root.reindexObjectSecurity()
        self.assertIn(self.workspace_guest.id, source)

    def test_only_users_with_local_roles_with_view_permissions_are_found_by_search(self):
        self.login(self.workspace_admin)
        source = ActualWorkspaceMembersSource(self.workspace)

        results = source.search(self.workspace_guest.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.workspace_guest.id, results[0].value)

        results = source.search(self.regular_user.id)
        self.assertEqual(0, len(results))

        # Assigning WorkspaceGuest to regular_user and check that he is then
        # found in the ActualWorkspaceMembersSource
        RoleAssignmentManager(self.workspace).add_or_update(
            self.regular_user.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)
        results = source.search(self.regular_user.id)
        self.assertEqual(1, len(results))
        self.assertEqual(self.regular_user.id, results[0].value)

        # Only local roles that give view permissions are considered for
        # users found in the ActualWorkspaceMembersSource
        self.workspace.manage_permission('View', roles=[])
        results = source.search(self.regular_user.id)
        self.assertEqual(0, len(results))

        results = source.search(self.workspace_guest.id)
        self.assertEqual(0, len(results))
