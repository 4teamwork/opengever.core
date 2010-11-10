from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.portlets.tree import treeportlet
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.setup.repositoryroot')
    transaction.commit()

    transmogrifier(u'opengever.setup.various')
    transaction.commit()

    # if '1' in context.getId():
    #     transmogrifier(u'opengever.setup.local_roles_m1')
    # else:
    #     transmogrifier(u'opengever.setup.local_roles_m2')
    # transaction.commit()


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

    if 'opengever-portlets-tree-TreePortlet' not in manager.keys():
        manager['opengever-portlets-tree-TreePortlet'] = \
            treeportlet.Assignment(root_path='ordnungssystem')


def import_various(setup):
    if setup.readDataFile('opengever.setup.txt') is None:
        return
    site = setup.getSite()
    start_import(site)
    settings(site)
