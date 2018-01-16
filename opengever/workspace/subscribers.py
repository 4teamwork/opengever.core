

def assign_owner_role_on_creation(workspace, event):
    """The creator of the workspace should have the WorkspaceOwner role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    roles = set(dict(workspace.get_local_roles()).get('owner_userid', ()))
    roles.add('WorkspaceOwner')
    workspace.manage_setLocalRoles(owner_userid, sorted(list(roles)))
