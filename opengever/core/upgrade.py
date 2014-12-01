from alembic.migration import MigrationContext
from alembic.operations import Operations
from ftw.upgrade import UpgradeStep
from opengever.ogds.base.utils import create_session
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
import logging


TRACKING_TABLE_NAME = 'opengever_upgrade_version'
logger = logging.getLogger('opengever.upgrade')


class IdempotentOperations(Operations):
    """Make alembic.operations tolerant to the same migration instruction being
    called multiple times.

    This might happen when a DB-migration has been executed halfway but then
    fails. Since MYSQL does not support transaction aware schema changes we
    have to handle these partially executed migrations by ourself.

    This class relies on an updated metadata, you have to do that manually
    in your schema migrations by calling `SchemaMigration.refresh_metadata`.

    """
    def __init__(self, schema_migration, migration_context):
        super(IdempotentOperations, self).__init__(migration_context)
        self.schema_migration = schema_migration
        self.metadata = self.schema_migration.metadata

    def _get_table(self, table_name):
        return self.metadata.tables.get(table_name)

    def _get_column(self, table_name, column_name):
        table = self._get_table(table_name)
        if table is None:
            return None
        return table.columns.get(column_name)

    def drop_column(self, table_name, column_name, **kw):
        if self._get_column(table_name, column_name) is None:
            logger.log(logging.INFO,
                       "Skipping drop colum '{0}' of table '{1}', "
                       "column does not exist"
                       .format(column_name, table_name))
            return

        super(IdempotentOperations, self).drop_column(
            table_name, column_name, **kw)

    def add_column(self, table_name, column, schema=None):
        column_name = column.name
        if self._get_column(table_name, column_name) is not None:
            logger.log(logging.INFO,
                       "Skipping add colum '{0}' to table '{1}', "
                       "column does already exist"
                       .format(column_name, table_name))
            return

        super(IdempotentOperations, self).add_column(
            table_name, column, schema)

    def create_table(self, name, *columns, **kw):
        if self._get_table(name) is not None:
            logger.log(logging.INFO,
                       "Skipping create table '{0}', table does already exist"
                       .format(name))
            return

        super(IdempotentOperations, self).create_table(name, *columns, **kw)


class DeactivatedFKConstraint(object):
    """Temporarily removes an FK-constraint.

    This is required when migrating a MySQL column that is part of a foreign
    key relationship.

    """
    def __init__(self, operations, name, source, referent,
                 source_cols, referent_cols):
        self.op = operations
        self.name = name
        self.source = source
        self.referent = referent
        self.source_cols = source_cols
        self.referent_cols = referent_cols

    def __enter__(self):
        self.op.drop_constraint(self.name, self.source, type='foreignkey')

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.op.create_foreign_key(self.name, self.source, self.referent,
                                   self.source_cols, self.referent_cols)
        return False


class SchemaMigration(UpgradeStep):
    """Baseclass for database-(schema) upgrade steps.

    Maintains a tracking table to make sure that a database migration is only
    run once. Configure as follows:
      - `profileid`:
        The opengever sub-package name for which the migration runs.
      - `upgradeid`:
        The target profile id.

    e.g.::

        class MyMigration(SchemaMigration):

            profileid = 'opengever.globalindex'
            upgradeid = 2701

            def migrate(self):
                # do stuff here!

    """
    profileid = None
    upgradeid = None

    def __call__(self):
        self._assert_configuration()
        self._setup_db_connection()
        self._create_tracking_table()
        self._insert_initial_version()
        if self._has_upgrades_to_install():
            self._log_do_migration()
            self.migrate()
            self._update_migrated_version()
        else:
            self._log_skipping_migration()

    def migrate(self):
        raise NotImplementedError()

    def execute(self, statement):
        return self.connection.execute(statement)

    def refresh_metadata(self):
        self.metadata.clear()
        self.metadata.reflect()

    def get_foreign_key_name(self, table_name, column_name):
        foreign_keys = self.op.metadata.tables.get(table_name).columns.get(column_name).foreign_keys
        assert len(foreign_keys) == 1
        return foreign_keys.pop().name

    def _log_skipping_migration(self):
        logger.log(logging.INFO,
                   'Skipping DB-migration {} -> {}, already installed'.format(
                       self.profileid, self.upgradeid))

    def _log_do_migration(self):
        logger.log(logging.INFO, 'Running DB-migration {} -> {}'.format(
            self.profileid, self.upgradeid))

    def _assert_configuration(self):
        assert self.profileid is not None, 'configure a profileid'
        assert self.upgradeid is not None, 'configure an upgradeid'
        assert int(self.upgradeid) > 0, 'upgradeid must be > 0'
        assert len(self.profileid) < 50, 'profileid max length is 50 chars'

    def _current_version(self):
        versions_table = self.metadata.tables.get(TRACKING_TABLE_NAME)
        current_version_row = self.execute(
            select([versions_table.c.upgradeid]).where(
                versions_table.c.profileid == self.profileid).distinct()
            ).fetchone()
        return current_version_row.upgradeid or 0

    def _has_upgrades_to_install(self):
        return self._current_version() < self.upgradeid

    def _create_tracking_table(self):
        if self.metadata.tables.get(TRACKING_TABLE_NAME, None) is not None:
            return

        self.op.create_table(
            TRACKING_TABLE_NAME,
            Column('profileid', String(50), primary_key=True),
            Column('upgradeid', Integer, nullable=False),
        )
        self.refresh_metadata()

    def _insert_initial_version(self):
        versions_table = self.metadata.tables.get(TRACKING_TABLE_NAME)
        result = self.execute(
            versions_table.select().where(
                versions_table.c.profileid == self.profileid)
            ).fetchall()
        if result:
            return

        self.execute(
            versions_table.insert().values(profileid=self.profileid,
                                           upgradeid=0))

    def _update_migrated_version(self):
        versions_table = self.metadata.tables.get(TRACKING_TABLE_NAME)
        self.execute(
            versions_table.update().values(upgradeid=self.upgradeid).
            where(versions_table.c.profileid == self.profileid)
        )

    def _setup_db_connection(self):
        session = create_session()
        engine = session.bind
        self.connection = engine.connect()
        self.migration_context = MigrationContext.configure(self.connection)
        self.metadata = MetaData(engine, reflect=True)
        self.op = IdempotentOperations(self, self.migration_context)
