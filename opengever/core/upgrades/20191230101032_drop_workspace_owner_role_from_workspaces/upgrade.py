from ftw.upgrade import UpgradeStep
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from plone import api


class DropWorkspaceOwnerRoleFromWorkspaces(UpgradeStep):
    """Update workspace workflows, drop WorkspaceOwner role.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_folder',
             'opengever_workspace_todo',
             'opengever_workspace_todolist',
             'opengever_workspace'],
            reindex_security=True)
        self.remove_workspace_owner_role()
        self.make_workspace_creators_admins()

    def remove_workspace_owner_role(self):
        # Remove global role assignments
        role_manager = api.portal.get_tool('acl_users').portal_role_manager
        if 'WorkspaceOwner' in role_manager._roles:
            role_manager.removeRole('WorkspaceOwner')

        # Remove the role from the site root __ac_roles__
        api.portal.get()._delRoles(['WorkspaceOwner'])

    def make_workspace_creators_admins(self):
        query = {'portal_type': 'opengever.workspace.workspace'}
        for workspace in self.objects(query, "Make workspace creatros admin"):
            owner_userid = workspace.Creator()
            assignment = SharingRoleAssignment(owner_userid, ['WorkspaceAdmin'])
            RoleAssignmentManager(workspace).add_or_update_assignment(assignment)
