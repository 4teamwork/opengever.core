from ftw.builder import Builder
from ftw.builder import create
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.sources import PotentialWorkspaceMembersSource
from opengever.ogds.base.sources import ActualWorkspaceMembersSource
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import IntegrationTestCase
from opengever.workspace.utils import get_workspace_user_ids
from opengever.workspace.utils import is_within_workspace


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


class TestAllUsersInboxesAndTeamsSourceForWorkspace(IntegrationTestCase):

    def setUp(self):
        super(TestAllUsersInboxesAndTeamsSourceForWorkspace, self).setUp()
        self.login(self.administrator)
        self.org_unit2 = create(Builder('org_unit')
                                .id('unit2')
                                .having(title=u'Finanzdirektion',
                                        admin_unit=get_current_admin_unit())
                                .with_default_groups())

        self.john = create(Builder('ogds_user')
                           .id('john')
                           .having(firstname=u'John', lastname=u'Doe')
                           .assign_to_org_units([get_current_org_unit()]))
        self.hugo = create(Builder('ogds_user')
                           .id('hugo')
                           .having(firstname=u'Hugo', lastname=u'Boss')
                           .assign_to_org_units([get_current_org_unit()]))
        self.hans = create(Builder('ogds_user')
                           .id('hans')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .assign_to_org_units([get_current_org_unit(),
                                                 self.org_unit2]))
        self.reto = create(Builder('ogds_user')
                           .id('reto')
                           .having(firstname=u'Reto', lastname=u'Rageto')
                           .assign_to_org_units([self.org_unit2]))

    def set_permissions_on_workspace(self):
        self.workspace.manage_permission('View', roles=['Contributor', ])

        RoleAssignmentManager(self.workspace).add_or_update_assignment(
            SharingRoleAssignment(self.hugo.userid, ['Contributor']))
        RoleAssignmentManager(self.workspace).add_or_update_assignment(
            SharingRoleAssignment(self.john.userid, ['Contributor']))

    def test_is_within_workspace(self):
        self.assertFalse(is_within_workspace(self.dossier),
                         'Dossier is not within workspace')
        self.assertFalse(is_within_workspace(self.workspace_root),
                         'WorkspaceRoot is not within workspace')

        self.assertTrue(is_within_workspace(self.workspace),
                        'Workspace is within Workspace')

        doc_in_workspace = create(Builder('document').within(self.workspace))
        self.assertTrue(is_within_workspace(doc_in_workspace),
                        'Document in workspace is within workspace')

    def test_get_workspace_user_ids(self):
        self.set_permissions_on_workspace()
        self.assertEquals([self.john.userid, self.hugo.userid],
                          get_workspace_user_ids(self.workspace))

    def test_only_local_roles_with_view_permission_are_selectable(self):
        source = AllUsersInboxesAndTeamsSource(self.workspace)
        self.assertNotIn(u'fa:john', source)
        self.assertNotIn(u'fa:hugo', source)
        self.assertNotIn(u'fa:hans', source)
        self.assertNotIn(u'unit2:hans', source)
        self.assertNotIn(u'unit2:reto', source)
        self.assertNotIn(u'unit2:john', source)

    def test_local_roles_from_workspace_are_in_source(self):
        self.set_permissions_on_workspace()
        source = AllUsersInboxesAndTeamsSource(self.workspace)

        self.assertIn(u'fa:john', source)
        self.assertIn(u'fa:hugo', source)
        self.assertIn(u'unit2:john', source)
        self.assertNotIn(u'fa:hans', source)
        self.assertNotIn(u'unit2:hans', source)
        self.assertNotIn(u'unit2:reto', source)

    def test_search_for_users_within_workspace(self):
        source = AllUsersInboxesAndTeamsSource(self.workspace)
        result = source.search('John')

        self.assertFalse(
            result,
            'Expect no result, since there are no permissions set.')

        self.set_permissions_on_workspace()

        result = source.search('John')
        self.assertEqual(1, len(result), 'Expect one result. only John')

        result = source.search('Hugo')
        self.assertEqual(1, len(result), 'Expect one result. only John')
