from alembic.migration import MigrationContext
from alembic.operations import Operations
from ftw.upgrade import UpgradeStep
from opengever.base.model import create_session
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
from zope.sqlalchemy.datamanager import mark_changed
import logging


TRACKING_TABLE_NAME = 'opengever_upgrade_version'

# Module global to keep a reference to the tracking table across several
# instances of SchemaMigration upgrade steps
_tracking_table = None

logger = logging.getLogger('opengever.upgrade')


class AbortUpgrade(Exception):
    """The upgrade had to be aborted for the reason specified in message."""


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

    def _has_index(self, indexname, tablename):
        table = self.metadata.tables.get(tablename)
        for index in table.indexes:
            if index.name == indexname:
                return True
        return False

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

        table = super(IdempotentOperations, self).create_table(
            name, *columns, **kw)
        return table

    def drop_constraint(self, name, table_name, type_=None, schema=None):
        if not self._has_index(name, table_name):
            logger.log(logging.INFO,
                       "Skipping drop constraint '{0}' for table '{1}', "
                       "constraint does not exists."
                       .format(name, table_name))
            return

        super(IdempotentOperations, self).drop_constraint(
            name, table_name, type_=type_, schema=schema)

    def create_unique_constraint(self, name, source, local_cols,
                                 schema=None, **kw):
        if self._has_index(name, source):
            logger.log(logging.INFO,
                       "Skipping create unique constraint '{0}' for table '{1}', "
                       "constraint already exists."
                       .format(name, source))
            return

        super(IdempotentOperations, self).create_unique_constraint(
            name, source, local_cols, schema, **kw)


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
        self.session = self._setup_db_connection()
        self._insert_initial_version()
        if self._has_upgrades_to_install():
            self._log_do_migration()
            self.migrate()
            self._update_migrated_version()
            # If the transaction contains only DDL statements, the transaction
            # isn't automatically marked as changed, so we do it ourselves
            mark_changed(self.session)

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
        table = self.metadata.tables.get(table_name)
        foreign_keys = table.columns.get(column_name).foreign_keys
        assert len(foreign_keys) == 1
        return foreign_keys.pop().name

    @property
    def is_oracle(self):
        return self.dialect_name == 'oracle'

    @property
    def is_postgres(self):
        return self.dialect_name == 'postgresql'

    @property
    def is_mysql(self):
        return self.dialect_name == 'mysql'

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

    def _get_tracking_table(self):
        """Fetches the tracking table from the DB schema metadata if present,
        or creates it if necessary.

        Once a reference to the tracking table has been obtained it's memoized
        in the module global `_tracking_table` and reused in further calls to
        this method.
        """
        global _tracking_table
        if _tracking_table is None:
            table = self.metadata.tables.get(TRACKING_TABLE_NAME)
            if table is None:
                table = self._create_tracking_table()
            _tracking_table = table
        return _tracking_table

    def _current_version(self):
        versions_table = self._get_tracking_table()
        current_version_row = self.execute(
            select([versions_table.c.upgradeid]).where(
                versions_table.c.profileid == self.profileid).distinct()
        ).fetchone()
        return current_version_row.upgradeid or 0

    def _has_upgrades_to_install(self):
        return self._current_version() < self.upgradeid

    def _create_tracking_table(self):
        tracking_table_definition = (
            TRACKING_TABLE_NAME,
            Column('profileid', String(50), primary_key=True),
            Column('upgradeid', Integer, nullable=False),
        )
        table = self.op.create_table(*tracking_table_definition)
        return table

    def _insert_initial_version(self):
        versions_table = self._get_tracking_table()
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
        versions_table = self._get_tracking_table()
        self.execute(
            versions_table.update().values(upgradeid=self.upgradeid).
            where(versions_table.c.profileid == self.profileid)
        )

    def _setup_db_connection(self):
        session = create_session()
        self.connection = session.connection()
        self.migration_context = MigrationContext.configure(self.connection)
        self.op = IdempotentOperations(self, self.migration_context)
        self.dialect_name = self.connection.dialect.name
        self.metadata = MetaData(self.connection, reflect=True)
        return session
