from opengever.base.model import create_session
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.sharing.local_roles_lookup.manager import LocalRolesLookupManager
from opengever.testing import IntegrationTestCase


class TestLocalRolesLookupManager(IntegrationTestCase):

    def test_can_add_new_entries_if_they_do_not_exist(self):
        session = create_session()
        map(session.delete, LocalRolesLookupManager().model_cls.query.all())

        self.assertEqual(0, LocalRolesLookupManager().model_cls.query.count())

        self.assertTrue(LocalRolesLookupManager().add('principal-1', 'uid-1', ['Editor']))
        self.assertTrue(LocalRolesLookupManager().add('principal-2', 'uid-1', ['Editor']))
        self.assertTrue(LocalRolesLookupManager().add('principal-2', 'uid-2', ['Editor']))

        self.assertFalse(LocalRolesLookupManager().add('principal-2', 'uid-2', ['Editor']))

        self.assertEqual(3, LocalRolesLookupManager().model_cls.query.count())

    def test_can_list_entries_by_principal_ids(self):
        LocalRolesLookupManager().add('user-1', 'uid-1', ['Editor'])
        LocalRolesLookupManager().add('user-1', 'uid-2', ['Editor'])
        LocalRolesLookupManager().add('group-1', 'uid-2', ['Editor'])
        LocalRolesLookupManager().add('group-1', 'uid-3', ['Editor'])

        LocalRolesLookupManager().add('user-2', 'uid-4', ['Editor'])

        uids = LocalRolesLookupManager().get_distinct_uids_by_principals(['user-1', 'group-1'])
        self.assertItemsEqual(['uid-1', 'uid-2', 'uid-3'], uids)

    def test_can_list_principal_ids_by_uid(self):
        LocalRolesLookupManager().add('user-1', 'uid-1', ['Editor'])
        LocalRolesLookupManager().add('user-1', 'uid-2', ['Editor'])
        LocalRolesLookupManager().add('group-1', 'uid-1', ['Editor'])
        LocalRolesLookupManager().add('user-2', 'uid-4', ['Editor'])

        principal_ids = LocalRolesLookupManager().get_distinct_principal_ids_by_uid('uid-1')
        self.assertItemsEqual(['user-1', 'group-1'], principal_ids)

    def test_add_entry_when_new_user_was_added_in_localroles(self):
        self.login(self.manager)

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

        # Add new user
        assignment = SharingRoleAssignment('user-1', ('Editor', ))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)
        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user', 'user-1'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

    def test_update_entry_when_existing_users_roles_have_been_changed(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        self.assertItemsEqual(
            ['TaskResponsible'],
            manager.get_entries(uids_filter=[self.dossier.UID()], principal_ids_filter=['regular_user'])[0].roles)

        # Update roles
        assignment = SharingRoleAssignment('regular_user', ('Editor', 'Reviewer', 'Owner'))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            ['Reviewer', 'Editor', 'TaskResponsible'],
            manager.get_entries(uids_filter=[self.dossier.UID()], principal_ids_filter=['regular_user'])[0].roles)

    def test_remove_entry_when_existing_user_does_not_have_any_managed_local_role(self):
        self.login(self.manager)

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

        # Remove users role assignments
        RoleAssignmentManager(self.dossier).clear_by_cause_and_principal(ASSIGNMENT_VIA_SHARING, 'robert.ziegler')

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

    def test_ignore_not_managed_portal_types(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        self.assertItemsEqual([], manager.get_distinct_uids_by_principals(['user-1']))

        managed_context = self.dossier
        not_managed_context = self.task

        self.assertIn(managed_context.portal_type, manager.MANAGED_PORTAL_TYPES)
        self.assertNotIn(not_managed_context.portal_type, manager.MANAGED_PORTAL_TYPES)

        assignment = SharingRoleAssignment('user-1', ('Editor', ))
        RoleAssignmentManager(not_managed_context).add_or_update_assignment(assignment)

        self.assertItemsEqual([], manager.get_distinct_uids_by_principals(['user-1']))

        assignment = SharingRoleAssignment('user-1', ('Editor', ))
        RoleAssignmentManager(managed_context).add_or_update_assignment(assignment)

        self.assertItemsEqual([managed_context.UID()], manager.get_distinct_uids_by_principals(['user-1']))

    def test_ignore_not_managed_roles(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user'],
            manager.get_distinct_principal_ids_by_uid(self.dossier.UID()))

        managed_role = 'Editor'
        not_managed_role = 'Owner'

        self.assertIn(managed_role, manager.MANAGED_ROLES)
        self.assertNotIn(not_managed_role, manager.MANAGED_ROLES)

        assignment = SharingRoleAssignment('user-1', (not_managed_role, ))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

        assignment = SharingRoleAssignment('user-1', (managed_role, ))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            ['fa_inbox_users', 'regular_user', 'user-1'],
            LocalRolesLookupManager().get_distinct_principal_ids_by_uid(self.dossier.UID()))

    def test_can_get_entries(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        assignment = SharingRoleAssignment('user-1', ('Editor', ))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            [
                '<LocalRole plone, archivist, createrepositorytree000000000001>',
                '<LocalRole plone, archivist, createrepositorytree000000000004>',
                '<LocalRole plone, archivist, createtreatydossiers000000000018>',
                '<LocalRole plone, beatrice.schrodinger, createworkspace00000000000000001>',
                '<LocalRole plone, dossier_manager, createrepositorytree000000000002>',
                '<LocalRole plone, fa_inbox_users, createexpireddossier000000000001>',
                '<LocalRole plone, fa_inbox_users, createinactivedossier00000000001>',
                '<LocalRole plone, fa_inbox_users, createprotecteddossiers000000003>',
                '<LocalRole plone, fa_inbox_users, createtreatydossiers000000000001>',
                '<LocalRole plone, fa_users, createrepositorytree000000000001>',
                '<LocalRole plone, fridolin.hugentobler, createworkspace00000000000000001>',
                '<LocalRole plone, gunther.frohlich, createworkspace00000000000000001>',
                '<LocalRole plone, hans.peter, createworkspace00000000000000001>',
                '<LocalRole plone, jurgen.konig, createrepositorytree000000000001>',
                '<LocalRole plone, regular_user, createexpireddossier000000000001>',
                '<LocalRole plone, regular_user, createinactivedossier00000000001>',
                '<LocalRole plone, regular_user, createprotecteddossiers000000003>',
                '<LocalRole plone, regular_user, createtreatydossiers000000000001>',
                '<LocalRole plone, robert.ziegler, createprotecteddossiers000000001>',
                '<LocalRole plone, robert.ziegler, createprotecteddossiers000000003>',
                '<LocalRole plone, user-1, createtreatydossiers000000000001>'
            ],
            [str(entry) for entry in manager.get_entries()])

    def test_get_entries_allows_to_filter_by_uids(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        assignment = SharingRoleAssignment('user-1', ('Editor', ))
        RoleAssignmentManager(self.dossier).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            [
                '<LocalRole plone, archivist, createrepositorytree000000000001>',
                '<LocalRole plone, fa_inbox_users, createtreatydossiers000000000001>',
                '<LocalRole plone, fa_users, createrepositorytree000000000001>',
                '<LocalRole plone, jurgen.konig, createrepositorytree000000000001>',
                '<LocalRole plone, regular_user, createtreatydossiers000000000001>',
                '<LocalRole plone, user-1, createtreatydossiers000000000001>'
            ],
            [str(entry) for entry in manager.get_entries([self.dossier.UID(), self.repository_root.UID()])])

    def test_get_entries_allows_to_filter_by_principal_ids(self):
        self.login(self.manager)
        manager = LocalRolesLookupManager()

        assignment = SharingRoleAssignment('regular_user', ('Editor', ))
        RoleAssignmentManager(self.repository_root).add_or_update_assignment(assignment)

        self.assertItemsEqual(
            [
                '<LocalRole plone, fa_users, createrepositorytree000000000001>',
                '<LocalRole plone, regular_user, createexpireddossier000000000001>',
                '<LocalRole plone, regular_user, createinactivedossier00000000001>',
                '<LocalRole plone, regular_user, createprotecteddossiers000000003>',
                '<LocalRole plone, regular_user, createrepositorytree000000000001>',
                '<LocalRole plone, regular_user, createtreatydossiers000000000001>'
            ],
            [str(entry) for entry in manager.get_entries(principal_ids_filter=['regular_user', 'fa_users'])])
