from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.portlets.tree import treeportlet
from plone.app.portlets.portlets import navigation
from plone.dexterity.utils import createContentInContainer
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
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
    manager = getUtility(IPortletManager, name=u'plone.leftcolumn',
                        context=context)
    mapping = getMultiAdapter((context, manager,),
                              IPortletAssignmentMapping)
    if 'navigation' in mapping.keys():
        del mapping[u'navigation']

    repository_root = context.REQUEST.get('repository_root', None)
    repository_root_name = repository_root[0]
    if 'opengever-portlets-tree-TreePortlet' not in mapping.keys():
        mapping['opengever-portlets-tree-TreePortlet'] = \
            treeportlet.Assignment(root_path=repository_root_name)

    # add a new navigation portlet at /eingangskorb
    inbox = context.restrictedTraverse('eingangskorb')
    mapping = getMultiAdapter((inbox, manager),
                              IPortletAssignmentMapping)
    if 'navigation' not in mapping.keys():
        mapping['navigation'] = navigation.Assignment(root='/eingangskorb',
                                                      currentFolderOnly=False,
                                                      includeTop=False,
                                                      topLevel=0,
                                                      bottomLevel=0)

    # block inherited context portlets on /eingangskorb
    assignable = getMultiAdapter((inbox, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

def import_various(setup):
    if setup.readDataFile('opengever.setup.txt') is None:
        return
    site = setup.getSite()
    create_repository_root(site)
    start_import(site)
    settings(site)
    mail_settings(setup)

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

def mail_settings(setup):
    site = setup.getSite()
    print site
    registry = getUtility(IRegistry, context=site)
    client_config=registry.forInterface(IClientConfiguration)
    client_id = client_config.client_id
    mail_config = registry.forInterface(IMailSettings)
    mail_domain = mail_config.mail_domain
    site.manage_changeProperties({'email_from_address':'noreply@'+mail_domain,
                                'email_from_name': client_id})
