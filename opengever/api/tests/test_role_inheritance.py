from ftw.testbrowser import browsing
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
import json


class TestRoleInheritanceGet(IntegrationTestCase):

    @browsing
    def test_role_inheritance_get_falsy(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(
            self.workspace_folder,
            view='@role-inheritance',
            headers=self.api_headers)
        self.assertEqual({'blocked': False}, browser.json)

    @browsing
    def test_role_inheritance_get_truthy(self, browser):
        self.login(self.administrator, browser)
        self.workspace_folder.__ac_local_roles_block__ = True

        browser.open(
            self.workspace_folder,
            view='@role-inheritance',
            headers=self.api_headers)
        self.assertEqual({'blocked': True}, browser.json)


class TestRoleInheritancePost(IntegrationTestCase):

    @browsing
    def test_block_workspace_folder_role_inheritance_with_copy_roles(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(
            self.workspace_folder,
            view='/@role-inheritance',
            data=json.dumps({'blocked': True, 'copy_roles': True}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual({'blocked': True}, browser.json)
        self.assertTrue(self.workspace_folder.__ac_local_roles_block__)

        workspace_manager = RoleAssignmentManager(self.workspace)
        folder_manager = RoleAssignmentManager(self.workspace_folder)

        self.assertEqual(
            workspace_manager.get_assignments_by_cause(ASSIGNMENT_VIA_SHARING),
            folder_manager.get_assignments_by_cause(ASSIGNMENT_VIA_SHARING),
            "Sharing assignment should be same as parent workspace"
        )

    @browsing
    def test_block_workspace_folder_role_inheritance_with_workspace_admin_will_copy_only_workspace_admin(self, browser):
        self.login(self.workspace_admin, browser)

        browser.open(
            self.workspace_folder,
            view='/@role-inheritance',
            data=json.dumps({'blocked': True}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual({'blocked': True}, browser.json)
        self.assertTrue(self.workspace_folder.__ac_local_roles_block__)

        folder_manager = RoleAssignmentManager(self.workspace_folder)
        assignments = folder_manager.get_assignments_by_cause(ASSIGNMENT_VIA_SHARING)
        self.assertEqual(
            [self.workspace_admin.id],
            [assignment.get('principal') for assignment in assignments],
            "Only the workspace admin should be the new principals for the folder"
        )

    @browsing
    def test_block_workspace_folder_role_inheritance_with_manager_will_copy_all_workspace_admins(self, browser):
        self.login(self.manager, browser)

        browser.open(
            self.workspace_folder,
            view='/@role-inheritance',
            data=json.dumps({'blocked': True}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual({'blocked': True}, browser.json)
        self.assertTrue(self.workspace_folder.__ac_local_roles_block__)

        folder_manager = RoleAssignmentManager(self.workspace_folder)
        assignments = folder_manager.get_assignments_by_cause(ASSIGNMENT_VIA_SHARING)
        self.assertItemsEqual(
            [self.workspace_owner.id, self.workspace_admin.id],
            [assignment.get('principal') for assignment in assignments],
            "Only workspace admins should be the new principals for the folder"
        )

    @browsing
    def test_unblock_workspace_folder_role_inheritance(self, browser):
        self.login(self.workspace_owner, browser)
        folder_manager = RoleAssignmentManager(self.workspace_folder)

        userid = self.workspace_owner.getId()
        assignment = SharingRoleAssignment(userid, ['WorkspaceAdmin'])
        folder_manager.add_or_update_assignment(assignment)
        self.workspace_folder.__ac_local_roles_block__ = True

        browser.open(
            self.workspace_folder,
            view='/@role-inheritance',
            data=json.dumps({'blocked': False}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual({'blocked': False}, browser.json)
        self.assertEqual(
            ([]),
            folder_manager.get_assignments_by_cause(ASSIGNMENT_VIA_SHARING),
            "Sharing assignment should have been cleared"
        )

    @browsing
    def test_members_cannot_change_inheritance(self, browser):
        self.login(self.workspace_member, browser)

        with browser.expect_unauthorized():
            browser.open(
                self.workspace_folder,
                view='/@role-inheritance',
                data=json.dumps({'blocked': True}),
                method='POST',
                headers=self.api_headers)

    @browsing
    def test_guests_cannot_change_inheritance(self, browser):
        self.login(self.workspace_member, browser)

        with browser.expect_unauthorized():
            browser.open(
                self.workspace_folder,
                view='/@role-inheritance',
                data=json.dumps({'blocked': True}),
                method='POST',
                headers=self.api_headers)
