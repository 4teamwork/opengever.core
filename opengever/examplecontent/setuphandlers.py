from Products.CMFCore.utils import getToolByName
from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.ogds.base.utils import get_current_client
import transaction

def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.examplecontent.repository')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.various')
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

    # set default layout
    context.get('aufgaben').setLayout('task-overview1')
    # set default page
    context.default_page = 'ordnungssystem'


def set_permissions(portal):
    # sets the permissions to the groups configuration in the client
    client = get_current_client()
    permissions = (
        ('/ordnungssystem', client.group, ('Contributor', 'Reader')),
        ('/eingangskorb', client.inbox_group,
         ('Contributor', 'Editor', 'Reader')))

    for path, principal, roles in permissions:
        if path.startswith('/'):
            path = path[1:]
        obj = portal.restrictedTraverse(path)
        obj.manage_setLocalRoles(principal, roles)

    wftool = getToolByName(portal, 'portal_workflow')
    wftool.updateRoleMappings(portal)


def setupVarious(setup):

    if setup.readDataFile('opengever.examplecontent.txt') is None:
        pass


    site = setup.getSite()
    start_import(site)
    settings(site)
    set_permissions(site)
