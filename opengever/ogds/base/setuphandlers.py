from Products.PluggableAuthService.interfaces import plugins
from opengever.ogds.base.model.client import Client
from opengever.ogds.base.model.user import User
from opengever.ogds.base.utils import create_session
from zope.interface import alsoProvides
from z3c.saconfig.interfaces import IScopedSession
from zope.component import queryUtility

from ftw.dictstorage.sql import DictStorageModel
from z3c.saconfig import named_scoped_session


def OpenGeverSessionName(object):
    return named_scoped_session('opengever')


MODELS = [User, Client, DictStorageModel]


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """

    # Only run step if a flag file is present
    if context.readDataFile('opengever.ogds.base.setuphandlers.txt') is None:
        return

    if queryUtility(IScopedSession, 'opengever'):
        create_sql_tables()


def create_sql_tables():
    """Creates the sql tables for the models.
    """

    session = create_session()
    for model in MODELS:
        getattr(model, 'metadata').create_all(session.bind)


def create_example(portal_setup):
    """Creates some example users and clients in the mysql db and in the
    acl_users folder.
    """

    # Only run step if a flag file is present
    if portal_setup.readDataFile(
        'opengever.ogds.base.create_users.txt') is None:
        return

    session = create_session()

    site = portal_setup.getSite()

    # USERS

    _create_example_user(session, site,
                         'hugo.boss',
                         {'firstname': 'Hugo',
                          'lastname': 'Boss'},
                         ('og_mandant1_users',))

    _create_example_user(session, site,
                         'peter.muster',
                         {'firstname': 'Peter',
                          'lastname': 'Muster'},
                         ('og_mandant2_users',))

    _create_example_user(session, site,
                         'franz.michel',
                         {'firstname': 'Franz',
                          'lastname': 'Michel'},
                         ('og_mandant1_users',
                          'og_mandant2_users'))

    # CLIENTS

    _create_example_client(session, 'mandant1',
                           {'title': 'Mandant 1',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://localhost:8080/mandant1',
                            'public_url': 'http://localhost:8080/mandant1',
                            'group': 'og_mandant1_users',
                            'inbox_group': 'og_mandant1_inbox'})

    _create_example_client(session, 'mandant2',
                           {'title': 'Mandant 2',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://127.0.0.1:8080/mandant2',
                            'public_url': 'http://127.0.0.1:8080/mandant2',
                            'group': 'og_mandant2_users',
                            'inbox_group': 'og_mandant2_inbox'})


def setup_pas_plugins(setup):
    """Install the PAS authentication plugins for verifying requests between
    clients.
    """

    portal = setup.getSite()
    if setup.readDataFile('opengever.ogds.base.pasplugins.txt') is None:
        return

    acl_users = portal.acl_users
    external_methods = {
        'extractCredentials': {
            'attrs': {
                'title': 'extractCredentials',
                'module': 'opengever.ogds.base.plugins',
                'function': 'extract_user'},
            'interface': plugins.IExtractionPlugin},
        'authenticateCredentials': {
            'attrs': {
                'title': 'authenticateCredentials',
                'module': 'opengever.ogds.base.plugins',
                'function': 'authenticate_credentials'},
            'interface' : plugins.IAuthenticationPlugin}
        }
    setup_scriptable_plugin(acl_users, 'octopus_tentacle_plugin',
                            external_methods)


def _create_example_user(session, site, userid, properties, groups):
    acl_users = site.acl_users
    password = 'demo09'

    # add the user to acl_users on site level
    if not acl_users.getUserById(userid):
        acl_users.source_users.addUser(userid, userid, password)

    # user should be in the given groups
    for groupid in groups:
        # does the group exist?
        group = acl_users.source_groups.getGroupById(groupid)
        if not group:
            acl_users.source_groups.addGroup(groupid)
            group = acl_users.source_groups.getGroupById(groupid)
        group.addMember(userid)

    # create the user object in sql
    if len(session.query(User).filter_by(userid=userid).all()) == 0:
        user = User(userid, **properties)
        session.add(user)

def _create_example_client(session, client_id, properties):
    if len(session.query(Client).filter_by(client_id=client_id).all()) == 0:
        client = Client(client_id, **properties)
        session.add(client)

def setup_scriptable_plugin(acl_users, plugin_id, external_methods):
    """Registers a scriptable plugin to the pas.
    """
    # --- register a PAS plugin
    if not acl_users.get(plugin_id, None):
        pas = acl_users.manage_addProduct['PluggableAuthService']
        pas.addScriptablePlugin(plugin_id)
    # --- register external methods
    plug = acl_users.get(plugin_id)
    em_factory = plug.manage_addProduct['ExternalMethod']
    activate_interfaces = []
    for em_id, em in external_methods.items():
        if not plug.get(em_id):
            # add the external method
            em_factory.manage_addExternalMethod(em_id, **em['attrs'])
        # provide the interface
        alsoProvides(plug, em['interface'])
        # activate the interface
        activate_interfaces.append(em['interface'].__name__)
    # activateInterfaces is destructive, so be careful, we dont wanna
    # disactivate interfaces which are currently active
    active_interfaces = []
    for info in plug.plugins.listPluginTypeInfo():
        if info['interface'].providedBy(plug):
            enabled = plug.plugins.listPlugins(info['interface'])
            if plug.getId() in [k for k,v in enabled]:
                active_interfaces.append(info['interface'].__name__)
    plug.manage_activateInterfaces(active_interfaces + activate_interfaces)
