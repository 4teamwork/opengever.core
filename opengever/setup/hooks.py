from Products.CMFCore.utils import getToolByName


def default_installed(site):
    set_global_roles(site)
    settings(site)
    disable_site_syndication(site)


def set_global_roles(site):
    assign_roles(site, ['og_administratoren'])


def settings(context):
    # remove stuff we dont want
    default_remove_ids = ('news', 'events', 'front-page')
    ids_to_remove = list(set(default_remove_ids) & set(context.objectIds()))
    context.manage_delObjects(ids_to_remove)

    # hide members
    if context.get('Members'):
        context.get('Members').setExcludeFromNav(True)
        context.get('Members').reindexObject()


def disable_site_syndication(context):
    ps = getToolByName(context, 'portal_syndication')
    ps.editProperties(isAllowed=False)


def assign_roles(context, admin_groups):
    prm = context.acl_users.portal_role_manager

    for admin_group in admin_groups:
        prm.assignRoleToPrincipal('Administrator', admin_group.strip())
        prm.assignRoleToPrincipal('Member', admin_group.strip())
        prm.assignRoleToPrincipal('Editor', admin_group.strip())
        prm.assignRoleToPrincipal('Role Manager', admin_group.strip())
        prm.assignRoleToPrincipal('Reviewer', admin_group.strip())
