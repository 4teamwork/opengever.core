from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.ldap_import.import_stamp import update_sync_stamp
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone.registry.interfaces import IRegistry
from sqlalchemy.orm.exc import NoResultFound
from zope.component import getUtility
from zope.component.hooks import getSite


def set_current_client_id(portal, clientid=u'client1'):
    if isinstance(clientid, str):
        clientid = clientid.decode('utf-8')

    registry = getUtility(IRegistry, context=portal)
    client = registry.forInterface(IClientConfiguration)
    client.client_id = clientid


def create_client(clientid='client1', session=None, **properties):
    session = session or create_session()

    defaults = {'title': clientid.capitalize(),
                'ip_address': '127.0.0.1',
                'site_url': 'http://nohost/%s' % clientid,
                'public_url': 'http://nohost/%s' % clientid,
                'group': '%s_users' % clientid,
                'inbox_group': '%s_inbox_users' % clientid}

    options = defaults.copy()
    options.update(properties)
    return _create_example_client(session, clientid, options)


def create_ogds_user(userid, session=None,
                     groups=('og_mandant1_users',), **properties):
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

    reset_ogds_sync_stamp(getSite())

    return user


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
