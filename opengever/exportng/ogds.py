from collections import namedtuple
from opengever.meeting.model import Meeting
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from sqlalchemy.sql.expression import false
import logging

logger = logging.getLogger('opengever.exportng')

Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type', 'getter'],
)
Attribute.__new__.__defaults__ = (None,)


class OGDSSyncer(object):

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata

    def get_sql_items(self):
        table = self.metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with self.engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_ogds_items(self):
        distinct_attr = getattr(self.model, self.key)
        return self.model.query.distinct(distinct_attr).all()

    def get_values(self, item):
        data = {}
        for attr in self.mapping:
            if attr.getter is not None:
                value = attr.getter(item, attr.name)
            else:
                value = getattr(item, attr.name)
            data[attr.col_name] = value
        return data

    def truncate(self):
        with self.engine.begin() as conn:
            conn.execution_options(autocommit=True).execute(
                "TRUNCATE TABLE {}".format(self.table))

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            inserts.append(self.get_values(item))

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


class UserSyncer(OGDSSyncer):

    table = 'users'
    model = User
    key = 'email'

    mapping = [
        Attribute('email', 'email', 'varchar'),
        Attribute('firstname', 'firstname', 'varchar'),
        Attribute('lastname', 'lastname', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


class GroupSyncer(OGDSSyncer):

    table = 'groups'
    model = Group
    key = 'groupname'

    mapping = [
        Attribute('groupname', 'groupname', 'varchar'),
        Attribute('title', 'title', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


def get_timezone(item, attr):
    return 'Europe/Zurich'


def get_dossier_uid(item, attr):
    oguid = getattr(item, attr)
    return oguid.resolve_object().UID()


def get_committee_uid(item, attr):
    committee = getattr(item, attr)
    return committee.resolve_committee().UID()


def get_meeting_id(item, attr):
    meeting_id = getattr(item, attr)
    return '{}-{}-{}-{}'.format(
        item.dossier_admin_unit_id,
        item.dossier_int_id,
        item.committee_id,
        meeting_id,
    )


class MeetingSyncer(OGDSSyncer):

    table = 'meetings'
    model = Meeting
    key = 'meeting_id'

    mapping = [
        Attribute('meeting_id', 'objexternalkey', 'varchar', get_meeting_id),
        Attribute('title', 'objsubject', 'varchar'),
        Attribute('start', 'mbegin', 'datetime'),
        Attribute('end', 'mend', 'datetime'),
        Attribute('location', 'mlocation', 'varchar'),
        Attribute('committee', 'mcommittee', 'varchar', get_committee_uid),
        Attribute('dossier_oguid', 'mdossier', 'varchar', get_dossier_uid),
        Attribute('start', 'mtimezone', 'varchar', get_timezone),
        Attribute('workflow_state', 'mmeetingstate', 'varchar'),
    ]
