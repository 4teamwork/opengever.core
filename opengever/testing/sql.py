from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.ldap_import.import_stamp import update_sync_stamp
from opengever.ogds.base.setup import create_example_client
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone.app.testing import TEST_USER_ID
from sqlalchemy.orm.exc import NoResultFound
from zope.component import getUtility
from zope.component.hooks import getSite
import warnings


def select_current_org_unit(unit_id='client1'):
    get_ou_selector().set_current_unit(unit_id)


# XXX remove me in favour of Builder('fixture')
def create_and_select_current_org_unit(unit_id='unit_a'):
    client = create_client(unit_id)
    create_ogds_user(TEST_USER_ID, assigned_client=[client],
                     firstname="Test", lastname="User")
    get_ou_selector().set_current_unit(unit_id)
    return get_ou_selector().get_current_unit()


def set_current_client_id(portal, clientid=u'client1'):
    """
    Creates a link between the current user (TEST_USER_ID)
    and the passed clientid (unit_id).

    This function is deprecated and should be replaced with
    select_current_org_unit or create_and_select_current_org_unit
    """
    warnings.warn("This function is deprecated. Use select_current_org_unit instead.",
                  DeprecationWarning, stacklevel=2)

    unit_id = clientid
    client = ogds_service().fetch_client(unit_id)
    if not client:
        client = create_client(unit_id)
        create_ogds_user(TEST_USER_ID, assigned_client=[client],
                         firstname="Test", lastname="User")
    get_ou_selector().set_current_unit(unit_id)


def create_client(clientid='client1', session=None, **properties):
    session = session or create_session()

    defaults = {'title': clientid.capitalize(),
                'group': '%s_users' % clientid,
                'inbox_group': '%s_inbox_users' % clientid}

    options = defaults.copy()
    options.update(properties)
    return create_example_client(session, clientid, options)


def create_ogds_user(userid, session=None,
                     groups=('og_mandant1_users',),
                     assigned_client=[], **properties):

    session = session or create_session()

    defaults = {'firstname': 'Hugo',
                'lastname': 'Boss',
                'email': 'hugo@boss.ch'}

    options = defaults.copy()
    options.update(properties)

    try:
        user = session.query(User).filter_by(userid=userid).one()
    except NoResultFound:
        user = User(userid, **options)
    else:
        for key, value in options.items():
            setattr(user, key, value)

    session.add(user)

    for groupid in groups:
        ogds_add_user_to_group(user, groupid, session=session)

    for client in assigned_client:
        assign_user_to_client(user, client, session=session)

    reset_ogds_sync_stamp(getSite())

    return user


def assign_user_to_client(user, client, session=None):
    session = session or create_session()
    client.users_group.users.append(user)
    session.add(client.users_group)


def reset_ogds_sync_stamp(portal):
    timestamp = update_sync_stamp(portal)
    getUtility(ISyncStamp).set_sync_stamp(timestamp, context=portal)


def ogds_add_user_to_group(user, groupid, session=None):
    session = session or create_session()

    try:
        group = session.query(Group).filter_by(groupid=groupid).one()
    except NoResultFound:
        group = Group(groupid)

    group.users.append(user)
    session.add(group)
