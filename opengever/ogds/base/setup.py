from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.base.model import Base
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from z3c.saconfig.interfaces import IScopedSession
from zope.component import queryUtility


def create_sql_tables():
    """Creates the sql tables for the models.
    """
    if not queryUtility(IScopedSession, 'opengever'):
        return

    session = create_session()
    Base.metadata.create_all(session.bind)
    DictStorageModel.metadata.create_all(session.bind)


def create_example_client(session, unit_id, properties):
    if len(session.query(OrgUnit).filter_by(unit_id=unit_id).all()) == 0:
        # Create users_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('group')).all()
        if len(temp) == 0:
            users_group = Group(properties.get('group'))
        else:
            users_group = temp[0]
        properties.pop('group')

        # Create inbox_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('inbox_group')).all()
        if len(temp) == 0:
            inbox_group = Group(properties.get('inbox_group'))
        else:
            inbox_group = temp[0]
        properties.pop('inbox_group')

        orgunit = OrgUnit(unit_id, **properties)
        orgunit.users_group = users_group
        orgunit.inbox_group = inbox_group
        session.add(orgunit)
        return orgunit
