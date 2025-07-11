from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from sqlalchemy.sql.expression import false
from collections import namedtuple
import logging

logger = logging.getLogger('opengever.exportng')

Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type'],
)


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
            data[attr.col_name] = getattr(item, attr.name)
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
