from opengever.base.role_assignments import InitialRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager


def assign_owner_role_on_creation(workspace, event):
    """The creator of the workspace should have the WorkspaceOwner role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    assignment = InitialRoleAssignment(owner_userid, ['WorkspaceOwner'])
    RoleAssignmentManager(workspace).add_assignment(assignment)
