from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment


def assign_owner_role_on_creation(workspace, event):
    """The creator of the workspace should have the WorkspaceOwner role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    assignment = SharingRoleAssignment(owner_userid, ['WorkspaceOwner'])
    RoleAssignmentManager(workspace).add_assignment(assignment)
