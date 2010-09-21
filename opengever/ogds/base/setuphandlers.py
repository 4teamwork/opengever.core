from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.user import User
from opengever.ogds.base.model.client import Client

MODELS = [User, Client]


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """

    # Only run step if a flag file is present
    if context.readDataFile('opengever.ogds.base.setuphandlers.txt') is None:
        return

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
                            'site_url': 'http://localhost:8080/mandant2',
                            'public_url': 'http://localhost:8080/mandant2',
                            'group': 'og_mandant2_users',
                            'inbox_group': 'og_mandant2_inbox'})


def _create_example_user(session, site, userid, properties, groups):
    acl_users = site.acl_users
    password = 'demo09'

    # add the user to acl_users on site level
    if not acl_users.getUserById(userid):
        acl_users.source_users.addUser(userid, userid, password)

    # user should be in the given groups
    for groupid in groups:
        # does the group exist?
        group = acl_users.getGroupById(groupid)
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
