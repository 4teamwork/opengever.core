from AccessControl.interfaces import IRoleManager
from AccessControl.Permission import Permission
from Acquisition import aq_base
from Acquisition import aq_chain
from operator import itemgetter
from plone import api


def roles_of_permission(context, permission):
    """Return all roles which have the given permission
    on the current context."""

    role_manager = IRoleManager(context)
    for p in role_manager.ac_inherited_permissions(1):
        name, value = p[:2]
        if name == permission:
            p = Permission(name, value, role_manager)
            roles = p.getRoles()
            return roles


def is_within_workspace_root(context):
    """ Checks, if the content is within the workspace root.
    """
    # Avoid circular imports
    from opengever.workspace.interfaces import IWorkspaceRoot
    return bool(filter(IWorkspaceRoot.providedBy, aq_chain(context)))


def is_within_workspace(context):
    """ Checks, if the content is a workspace or is within the workspace.
    """
    # Avoid circular imports
    from opengever.workspace.interfaces import IWorkspace
    return bool(filter(IWorkspace.providedBy, aq_chain(context)))


def get_containing_workspace(context):
    """ Returns the containing workspace of the current context
    """
    # Avoid circular imports
    from opengever.workspace.interfaces import IWorkspace
    workspace = filter(IWorkspace.providedBy, aq_chain(context))
    return workspace[0] if workspace else None


def get_workspace_user_ids(context, disregard_block=False):
    return get_workspace_actor_ids(context, 'user', disregard_block)


def get_workspace_actor_ids(context, actor_type, disregard_block=False, ):
    """ Walks up the Acquisition chain and collects all userids assigned
    to a role with the View permission.
    """
    containing_workspace = get_containing_workspace(context)
    if not containing_workspace:
        return []

    actor_ids = set([])
    allowed_roles_to_view = roles_of_permission(containing_workspace, 'View')
    portal = api.portal.get()

    def is_valid_actorid(valid_role_type, actor, roles, role_type, name):
        return role_type == valid_role_type and set(roles) & set(allowed_roles_to_view)

    for content in aq_chain(containing_workspace):
        if aq_base(content) == aq_base(portal):
            break
        actorroles = portal.acl_users._getLocalRolesForDisplay(content)
        actor_ids = actor_ids.union(set(
            map(itemgetter(0),
                filter(lambda args: is_valid_actorid(actor_type, *args), actorroles))))

        if getattr(aq_base(containing_workspace), '__ac_local_roles_block__', None) \
                and not disregard_block:
            break

    return list(actor_ids)
