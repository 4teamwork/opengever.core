from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.usermigration.localroles import migrate_localroles
from ftw.usermigration.browser import migration


class TestMigrateLocalRoles(IntegrationTestCase):

    def test_patch_applied(self):
        self.assertIs(
            migration.BUILTIN_MIGRATIONS['localroles'], migrate_localroles)

    def test_move_inbox_local_roles_of_existing_user(self):
        self.login(self.manager)
        old_id = self.secretariat_user.getId()
        manager = RoleAssignmentManager(self.inbox)

        assignments = manager.get_assignments_by_principal_id(old_id)
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)
        self.assertEqual([], manager.get_assignments_by_principal_id('new_user.id'))

        mapping = {old_id: 'new_user.id'}
        results = migrate_localroles(self.inbox, mapping, mode='move')

        self.assertEqual(
            [('/plone/eingangskorb', old_id, 'new_user.id')],
            results['moved'])
        self.assertEqual([], results['copied'])
        self.assertEqual([], results['deleted'])

        self.assertEqual([], manager.get_assignments_by_principal_id(old_id))
        assignments = manager.get_assignments_by_principal_id('new_user.id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)

    def test_migrate_local_roles_of_nonexisting_user(self):
        self.login(self.manager)
        mapping = {'spam': 'peter'}
        results = migrate_localroles(self.inbox, mapping)
        self.assertEquals([], results['moved'])
        self.assertEquals([], results['copied'])
        self.assertEquals([], results['deleted'])

    def test_delete_inbox_local_roles(self):
        self.login(self.manager)
        old_id = self.secretariat_user.getId()
        manager = RoleAssignmentManager(self.inbox)

        assignments = manager.get_assignments_by_principal_id(old_id)
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)
        self.assertEqual([], manager.get_assignments_by_principal_id('new_user.id'))

        mapping = {old_id: 'new_user.id'}
        results = migrate_localroles(self.inbox, mapping, mode='delete')

        self.assertEqual([], results['moved'])
        self.assertEqual([], results['copied'])
        self.assertEqual(
            [('/plone/eingangskorb', old_id, None)],
            results['deleted'])

        self.assertEqual([], manager.get_assignments_by_principal_id(old_id))
        self.assertEqual([], manager.get_assignments_by_principal_id('new_user.id'))

    def test_copy_inbox_local_roles(self):
        self.login(self.manager)
        old_id = self.secretariat_user.getId()
        manager = RoleAssignmentManager(self.inbox)

        assignments = manager.get_assignments_by_principal_id(old_id)
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)
        self.assertEqual([], manager.get_assignments_by_principal_id('new_user.id'))

        mapping = {old_id: 'new_user.id'}
        results = migrate_localroles(self.inbox, mapping, mode='copy')

        self.assertEqual([], results['moved'])
        self.assertEqual(
            [('/plone/eingangskorb', old_id, 'new_user.id')],
            results['copied'])
        self.assertEqual([], results['deleted'])

        assignments = manager.get_assignments_by_principal_id(old_id)
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)
        assignments = manager.get_assignments_by_principal_id('new_user.id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)

    def test_migrate_local_roles_of_multiple_users_on_plone_site(self):
        self.login(self.manager)
        old_secretariat_id = self.secretariat_user.getId()
        old_user_id = self.regular_user.getId()
        old_administrator_id = self.administrator.getId()

        mapping = {
            old_secretariat_id: 'new_secretariat_id',
            old_administrator_id: 'new_administrator_id',
            old_user_id: 'new_user_id'
        }
        results = migrate_localroles(self.portal, mapping)
        self.assertEqual([], results['copied'])
        self.assertEqual([], results['deleted'])
        moved = results['moved']
        self.assertItemsEqual(
            moved, set(moved),
            "Items should only appear once in migration statistics.")

        self.assertIn(
            ('/plone/ordnungssystem', old_secretariat_id, 'new_secretariat_id'),
            moved)
        manager = RoleAssignmentManager(self.repository_root)
        assignments = manager.get_assignments_by_principal_id('new_secretariat_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Reviewer', 'Publisher'],
                         assignments[0].roles)

        self.assertIn(
            ('/plone/vorlagen', old_administrator_id, 'new_administrator_id'),
            moved)
        manager = RoleAssignmentManager(self.templates)
        assignments = manager.get_assignments_by_principal_id('new_administrator_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Reader', 'Contributor', 'Editor'],
                         assignments[0].roles)
        self.assertIn(
            'user:new_administrator_id',
            index_data_for(self.templates)['allowedRolesAndUsers'])

        self.assertIn(
            ('/plone/vorlagen/vorlagen-neu', old_administrator_id, 'new_administrator_id'),
            moved)
        manager = RoleAssignmentManager(self.subtemplates)
        assignments = manager.get_assignments_by_principal_id('new_administrator_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Reader', 'Contributor', 'Editor'],
                         assignments[0].roles)
        self.assertIn(
            'user:new_administrator_id',
            index_data_for(self.subtemplates)['allowedRolesAndUsers'])

        self.assertIn(
            ('/plone/opengever-meeting-committeecontainer', old_administrator_id, 'new_administrator_id'),
            moved)
        manager = RoleAssignmentManager(self.committee_container)
        assignments = manager.get_assignments_by_principal_id('new_administrator_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['CommitteeAdministrator'],
                         assignments[0].roles)
        self.assertIn(
            'user:new_administrator_id',
            index_data_for(self.committee_container)['allowedRolesAndUsers'])

        self.assertIn(
            ('/plone/eingangskorb', old_secretariat_id, 'new_secretariat_id'),
            moved)
        manager = RoleAssignmentManager(self.inbox)
        assignments = manager.get_assignments_by_principal_id('new_secretariat_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Contributor', 'Editor', 'Reader'],
                         assignments[0].roles)
        self.assertIn(
            'user:new_secretariat_id',
            index_data_for(self.inbox)['allowedRolesAndUsers'])

        self.assertIn(
            ('/plone/private/kathi-barfuss', old_user_id, 'new_user_id'),
            moved)
        manager = RoleAssignmentManager(self.private_folder)
        assignments = manager.get_assignments_by_principal_id('new_user_id')
        self.assertEqual(1, len(assignments))
        self.assertEqual(['Publisher', 'Contributor', 'Reader', 'Owner',
                          'Reviewer', 'Editor'],
                         assignments[0].roles)
        self.assertIn(
            'user:new_user_id',
            index_data_for(self.private_folder)['allowedRolesAndUsers'])
