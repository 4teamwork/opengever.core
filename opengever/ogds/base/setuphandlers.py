from Products.PluggableAuthService.interfaces import plugins
from ftw.dictstorage.sql import DictStorageModel
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group, groups_users
from opengever.ogds.models.user import User
from z3c.saconfig import named_scoped_session
from z3c.saconfig.interfaces import IScopedSession
from zope.component import queryUtility
from zope.interface import alsoProvides
import transaction


def OpenGeverSessionName(object):
    return named_scoped_session('opengever')


MODELS = [User, Group, groups_users, Client, DictStorageModel]


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
    BASE.metadata.create_all(session.bind)

    DictStorageModel.metadata.create_all(session.bind)


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
            'interface': plugins.IAuthenticationPlugin}
        }
    setup_scriptable_plugin(acl_users, 'octopus_tentacle_plugin',
                            external_methods)


def _create_example_user(session, site, userid, properties, groups):
    acl_users = site.acl_users
    password = 'demo09'
    # add the user to acl_users on site level
    if not acl_users.getUserById(userid):
        acl_users.source_users.addUser(userid, userid, password)

    # create the user object in sql
    if session.query(User).filter_by(userid=userid).count() == 0:
        user = User(userid, **properties)
        session.add(user)
    else:
        user = session.query(User).filter_by(userid=userid).first()

    # append the user to the group
    for groupid in groups:
        groups = session.query(Group).filter(Group.groupid == groupid).all()
        # does the group don't exist create it
        if len(groups) == 0:
            group = Group(groupid)
            group.users.append(user)
            session.add(group)
        else:
            groups[0].users.append(user)
            session.add(groups[0])

    transaction.commit()

    return session.query(User).filter_by(userid=userid).first()


def _create_example_client(session, client_id, properties):
    if len(session.query(Client).filter_by(client_id=client_id).all()) == 0:

        #create users_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('group')).all()
        if len(temp) == 0:
            users_group = Group(properties.get('group'))
        else:
            users_group = temp[0]
        properties.pop('group')

        #create inbox_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('inbox_group')).all()
        if len(temp) == 0:
            inbox_group = Group(properties.get('inbox_group'))
        else:
            inbox_group = temp[0]
        properties.pop('inbox_group')

        client = Client(client_id, **properties)
        client.users_group = users_group
        client.inbox_group = inbox_group
        session.add(client)
        return client


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
            if plug.getId() in [k for k, v in enabled]:
                active_interfaces.append(info['interface'].__name__)
    plug.manage_activateInterfaces(active_interfaces + activate_interfaces)
