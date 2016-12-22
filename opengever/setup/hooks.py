from opengever.private import MEMBERSFOLDER_ID
from plone import api
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
    reorder_css_resources(site)


def default_content_installed(site):
    assign_default_navigation_portlet(site, 'eingangskorb')
    assign_default_navigation_portlet(site, 'vorlagen')
    assign_default_navigation_portlet(site, 'kontakte')
    block_context_portlets(site, MEMBERSFOLDER_ID)


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
    """Add a new navigation portlet to content."""

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
            topLevel=1,
            bottomLevel=0)

    # Block inherited context portlets on content
    assignable = getMultiAdapter(
        (content, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def block_context_portlets(site, content_id):
    content = site.restrictedTraverse(content_id)
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=content)

    # Block inherited context portlets on content
    assignable = getMultiAdapter(
        (content, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def reorder_css_resources(site):
    """The aim of reordering the CSS resources is to make as large
    bundles as possible, so that the client needs as few requests
    as possible to load the CSS.
    """
    registry = api.portal.get_tool('portal_css')

    # Ship all resources with "link", no "inline" anymore.
    for resource in registry.getResources():
        resource.setRendering('link')

    # Move all css resources, wich are disabled when diazo is disabled
    # to the top, in order to not have them in between other
    # resources which could possibly be bundled together.
    # This is done without changing the order in between those
    # resources.
    expression = 'not:request/HTTP_X_THEME_ENABLED | nothing'
    hidden = filter(lambda resource: resource.getExpression() == expression,
                    registry.getResources())
    for resource in reversed(hidden):
        registry.moveResourceToTop(resource.getId())

    # IEFixes has an diazo expression but also an IE conditional comment.
    # Move it to bottom in order to have it at the bottom of the diazo
    # block after the next step.
    registry.moveResourceToBottom('IEFixes.css')
    registry.moveResourceToBottom(
        '++theme++plonetheme.teamraum/css/iefixes.css')

    # Remove all "authenticated" conditions
    for resource in registry.getResources()[:]:
        if resource.getAuthenticated():
            resource.setAuthenticated(False)

    # Disable RTL CSS, we don't support RTL
    registry.getResource('RTL.css').setEnabled(False)

    # Remove `enabled diazo` expression
    expression = 'request/HTTP_X_THEME_ENABLED | nothing'
    hidden = filter(lambda resource: resource.getExpression() == expression,
                    registry.getResources())
    for resource in reversed(hidden):
        resource.setExpression('')

    # Move print.css to bottom (distinct "media"; can be loaded late)
    registry.moveResourceToBottom('print.css')


def reorder_js_resources(site):
    """The aim of reordering the JS resources is to make as large
    bundles as possible, so that the client needs as few requests
    as possible to load the JS.
    """
    registry = api.portal.get_tool('portal_javascripts')

    # Move all authenticated resources together to form one bundle.
    for resource in registry.getResources()[:]:
        if resource.getAuthenticated():
            registry.moveResourceToBottom(resource.getId())
