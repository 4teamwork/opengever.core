from AccessControl.interfaces import IRoleManager
from AccessControl.Permission import Permission
from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_parent
from Acquisition import aq_inner
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

    if context.getId() not in aq_parent(aq_inner(context)):
        # Creating a new object through the REST-API will create a temporary
        # object first. Then it validates all the field values and adds the
        # new context to the container.
        #
        # While validating the schema, the context will be the temporary
        # workspace instead the container object which is the assumed context.
        #
        # This behavior differs to content-creation without the REST-API. So we
        # have to change the context here if we have a temporary context.
        #
        # Unfortunately, there is no other way to detect a temporary object
        # than checking, if the current object is already added to the parent
        # object.
        #
        # See: https://github.com/plone/plone.restapi/blob/3.7.2/src/plone/restapi/services/content/add.py#L83
        context = aq_parent(aq_inner(context))

    return bool(filter(IWorkspace.providedBy, aq_chain(context)))


def get_workspace_user_ids(context):
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

        if getattr(aq_base(context), '__ac_local_roles_block__', None):
            break

    return list(users)
