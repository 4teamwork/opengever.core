from Products.CMFCore.utils import getToolByName
from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.ogds.base.utils import get_current_client
from opengever.portlets.tree import treeportlet
import transaction

def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.examplecontent.repository')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.various')
    transaction.commit()
    
    transmogrifier(u'opengever.examplecontent.templates')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.contacts')
    transaction.commit()

    if '1' in context.getId():
        transmogrifier(u'opengever.examplecontent.local_roles_m1')
    else:
        transmogrifier(u'opengever.examplecontent.local_roles_m2')
    transaction.commit()

    # transmogrifier(u'opengever.examplecontent.users')
    # transaction.commit()

def settings(context):
    # remove stuff we dont want
    default_remove_ids = ('news', 'events', 'front-page')
    ids_to_remove = list(set(default_remove_ids) & set(context.objectIds()))
    context.manage_delObjects(ids_to_remove)

    # exclude items from the navigation we not used
    if context.get('Members'):
        context.get('Members').setExcludeFromNav(True)
        context.get('Members').reindexObject()

    # replace unused navigation portlet with the tree portlet
    from zope.component import getUtility
    from zope.component import getMultiAdapter
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.interfaces import IPortletAssignmentMapping

    column = getUtility(IPortletManager, name=u'plone.leftcolumn', context=context)
    manager = getMultiAdapter((context, column,), IPortletAssignmentMapping)
    if 'navigation' in manager.keys():
        del manager[u'navigation']

    if 'opengever-portlets-tree-TreePortlet' not in manager.keys():
        manager['opengever-portlets-tree-TreePortlet'] = treeportlet.Assignment(root_path='ordnungssystem')

def setupVarious(setup):
    # if setup.readDataFile('opengever.examplecontent.txt') is None:
    #     return
    site = setup.getSite()
    start_import(site)
    settings(site)
