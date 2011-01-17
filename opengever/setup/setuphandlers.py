from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.portlets.tree import treeportlet
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.dexterity.utils import createContentInContainer
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

    transmogrifier(u'opengever.setup.local_roles')
    transaction.commit()


def settings(context):
    # remove stuff we dont want
    default_remove_ids = ('news', 'events', 'front-page')
    ids_to_remove = list(set(default_remove_ids) & \
                             set(context.objectIds()))
    context.manage_delObjects(ids_to_remove)

    # hide members
    if context.get('Members'):
        context.get('Members').setExcludeFromNav(True)
        context.get('Members').reindexObject()

    # replace unused navigation portlet with the tree portlet
    column = getUtility(IPortletManager, name=u'plone.leftcolumn',
                        context=context)
    manager = getMultiAdapter((context, column,),
                              IPortletAssignmentMapping)
    if 'navigation' in manager.keys():
        del manager[u'navigation']

    repository_root = context.REQUEST.get('repository_root', None)
    repository_root_name = repository_root[0]
    if 'opengever-portlets-tree-TreePortlet' not in manager.keys():
        manager['opengever-portlets-tree-TreePortlet'] = \
            treeportlet.Assignment(root_path=repository_root_name)


def import_various(setup):
    if setup.readDataFile('opengever.setup.txt') is None:
        return
    site = setup.getSite()
    create_repository_root(site)
    start_import(site)
    settings(site)

def set_global_roles(setup):
    admin_file = setup.readDataFile('administrator.txt')
    if admin_file is None:
        return
    site = setup.getSite()
    assign_roles(site, admin_file)

def assign_roles(context, admin_file):
    admin_groups= admin_file.split('\n')
    for admin_group in admin_groups:
        context.acl_users.portal_role_manager.assignRoleToPrincipal('Manager', admin_group.strip())
