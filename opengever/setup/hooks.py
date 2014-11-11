from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility


def default_installed(site):
    set_global_roles(site)
    settings(site)
    disable_site_syndication(site)


def default_content_installed(site):
    assign_default_navigation_portlet(site, 'eingangskorb')
    assign_default_navigation_portlet(site, 'vorlagen')


def repository_root_installed(site):
    pass


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


def assign_default_navigation_portlet(context, content_id):
    # Add a new navigation portlet to content
    content = context.restrictedTraverse(content_id)
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=content)
    mapping = getMultiAdapter((content, manager),
                              IPortletAssignmentMapping)
    if 'navigation' not in mapping.keys():
        mapping['navigation'] = navigation.Assignment(
            root=None,
            currentFolderOnly=False,
            includeTop=False,
            topLevel=0,
            bottomLevel=0)

    # Block inherited context portlets on content
    assignable = getMultiAdapter(
        (content, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
