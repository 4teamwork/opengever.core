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


def is_within_workspace(context):
    """ Checks, if the content is a workspace or is within the workspace.
    """
    # Avoid circular imports
    from opengever.workspace.interfaces import IWorkspace
    return bool(filter(IWorkspace.providedBy, aq_chain(context)))


def get_workspace_user_ids(context, disregard_block=False):
    """ Walks up the Acquisition chain and collects all userids assigned
    to a role with the View permission.
    """
    if not is_within_workspace(context):
        return []

    users = set([])
    allowed_roles_to_view = roles_of_permission(context, 'View')
    portal = api.portal.get()

    def is_valid_userid(*args):
        user, roles, role_type, name = args
        return role_type == u'user' and set(roles) & set(allowed_roles_to_view)

    for content in aq_chain(context):
        if aq_base(content) == aq_base(portal):
            break
        userroles = portal.acl_users._getLocalRolesForDisplay(content)
        users = users.union(set(
            map(itemgetter(0),
                filter(lambda args: is_valid_userid(*args), userroles))))
        if getattr(aq_base(context), '__ac_local_roles_block__', None) and not disregard_block:
            break

    return list(users)
