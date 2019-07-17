from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


def assign_owner_role_on_creation(workspace, event):
    """The creator of the workspace should have the WorkspaceOwner role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    assignment = SharingRoleAssignment(owner_userid, ['WorkspaceOwner'])
    RoleAssignmentManager(workspace).add_or_update_assignment(assignment)


def check_delete_preconditions(todolist, event):
    """Its only possible to remove todolist if they are empty.
    """

    # Ignore plone site deletions
    if IPloneSiteRoot.providedBy(event.object):
        return

    if len(todolist.objectValues()):
        raise ValueError(
            'The todolist is not empty, therefore deletion is not allowed.')
