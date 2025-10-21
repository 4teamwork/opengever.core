from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.base.model import Session
from opengever.ogds.base.setup import create_example_client
from opengever.ogds.base.setup import create_sql_tables
from opengever.ogds.models.group import Group
from opengever.ogds.models.group_membership import groups_users
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
import transaction


def default_installed(site):
    create_sql_tables()


def example_installed(site):
    _create_example(site)


def get_opengever_session(object):
    return Session


MODELS = [User, Group, groups_users, OrgUnit, DictStorageModel]


def _create_example(site):
    """Creates some example users and clients in the mysql db and in the
    acl_users folder.
    """
    session = create_session()

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

    create_example_client(session, 'mandant1',
                          {'title': 'Mandant 1',
                           'ip_address': '127.0.0.1',
                           'site_url': 'http://localhost:8080/mandant1',
                           'public_url': 'http://localhost:8080/mandant1',
                           'group': 'og_mandant1_users',
                           'inbox_group': 'og_mandant1_inbox'})

    create_example_client(session, 'mandant2',
                          {'title': 'Mandant 2',
                           'ip_address': '127.0.0.1',
                           'site_url': 'http://127.0.0.1:8080/mandant2',
                           'public_url': 'http://127.0.0.1:8080/mandant2',
                           'group': 'og_mandant2_users',
                           'inbox_group': 'og_mandant2_inbox'})


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
