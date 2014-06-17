from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.portlets.tree import treeportlet
from plone.app.portlets.portlets import navigation
from plone.dexterity.utils import createContentInContainer
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


def create_repository_root(context):
    repository_root = context.REQUEST.get('repository_root', None)
    if not repository_root:
        repository_root = ('ordnungssystem', 'Ordnungssystem')
        context.REQUEST.set('repository_root', repository_root)
    name, title = repository_root
    # first use name as title for forcing that name, then change the title
    obj = createContentInContainer(context,
                                   'opengever.repository.repositoryroot',
                                   checkConstraints=True, title=name)
    obj.setTitle(title)
    obj.reindexObject()


def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.setup.various')
    transaction.commit()

    transmogrifier(u'opengever.setup.templates')
    transaction.commit()

    # check if the setup should set local roles also one the repo root
    if context.REQUEST.get('local_roles') == '1':
        transmogrifier(u'opengever.setup.local_roles_with_repo')
    else:
        transmogrifier(u'opengever.setup.local_roles')

    transaction.commit()


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


def set_global_roles(setup):
    admin_file = setup.readDataFile('administrator.txt')
    if admin_file is None:
        return
    site = setup.getSite()
    assign_roles(site, admin_file)


def assign_roles(context, admin_file):
    admin_groups = admin_file.split('\n')
    prm = context.acl_users.portal_role_manager

    for admin_group in admin_groups:
        prm.assignRoleToPrincipal('Administrator', admin_group.strip())
        prm.assignRoleToPrincipal('Member', admin_group.strip())
        prm.assignRoleToPrincipal('Editor', admin_group.strip())
        prm.assignRoleToPrincipal('Role Manager', admin_group.strip())
        prm.assignRoleToPrincipal('Reviewer', admin_group.strip())


def assign_tree_portlet(context, root_path, remove_nav=False,
                        block_inheritance=False):
    # Assign tree portlet to given context
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=context)
    mapping = getMultiAdapter((context, manager,), IPortletAssignmentMapping)
    if 'opengever-portlets-tree-TreePortlet' not in mapping.keys():
        mapping['opengever-portlets-tree-TreePortlet'] = \
            treeportlet.Assignment(root_path=root_path)

    if remove_nav:
        # Remove unused navigation portlet
        if 'navigation' in mapping.keys():
            del mapping[u'navigation']

    if block_inheritance:
        # Block inherited context portlets
        assignable = getMultiAdapter(
            (context, manager), ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def assign_portlets(context):
    site = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(context, 'portal_catalog')
    repo_roots = catalog(portal_type="opengever.repository.repositoryroot")

    # Determine how many repository roots there are and
    # which one should be considered the main repo
    repository_root = context.REQUEST.get('repository_root', None)
    if repository_root:
        # We're creating a new client
        main_repo_root = repository_root[0]
    else:
        # We're in an upgrade step on an existing client
        if 'ordnungssystem2' in [r.id for r in repo_roots]:
            main_repo_root = 'ordnungssystem2'
        elif 'ordnungssystem' in [r.id for r in repo_roots]:
            main_repo_root = 'ordnungssystem'
        else:
            main_repo_root = repo_roots and repo_roots[0].id or None

    secondary_repo_roots = [
        r.id for r in repo_roots if not r.id == main_repo_root]

    if main_repo_root:
        # Assign tree portlet with main repo root to site root
        assign_tree_portlet(context=site, root_path=main_repo_root,
                            remove_nav=True, block_inheritance=False)

    for repo_name in secondary_repo_roots:
        repo = context.restrictedTraverse(repo_name)
        # Assign tree portlet to secondary repo root
        assign_tree_portlet(context=repo, root_path=repo_name,
                            remove_nav=True, block_inheritance=True)

    # Add a new navigation portlet at /eingangskorb
    inbox = context.restrictedTraverse('eingangskorb')
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=inbox)
    mapping = getMultiAdapter((inbox, manager),
                              IPortletAssignmentMapping)
    if 'navigation' not in mapping.keys():
        mapping['navigation'] = navigation.Assignment(root=None,
                                                      currentFolderOnly=False,
                                                      includeTop=False,
                                                      topLevel=0,
                                                      bottomLevel=0)

    # Block inherited context portlets on /eingangskorb
    assignable = getMultiAdapter(
        (inbox, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

    # Add a new navigation portlet at template dossier /vorlagen
    templatedossier = context.restrictedTraverse('vorlagen')
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=templatedossier)
    mapping = getMultiAdapter((templatedossier, manager),
                              IPortletAssignmentMapping)
    if 'navigation' not in mapping.keys():
        mapping['navigation'] = navigation.Assignment(
            root=None,
            currentFolderOnly=False,
            includeTop=False,
            topLevel=0,
            bottomLevel=0)

    # Block inherited context portlets on /vorlagen
    assignable = getMultiAdapter(
        (templatedossier, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def import_various(setup):
    if setup.readDataFile('opengever.setup.txt') is None:
        return
    site = setup.getSite()
    create_repository_root(site)
    start_import(site)
    settings(site)
    assign_portlets(site)
    disable_site_syndication(site)
