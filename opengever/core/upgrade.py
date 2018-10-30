from alembic.migration import MigrationContext
from alembic.operations import Operations
from decorator import decorator
from ftw.upgrade import UpgradeStep
from ftw.upgrade.directory.recorder import UpgradeStepRecorder
from opengever.base.model import create_session
from plone.memoize import forever
from Products.CMFCore.utils import getToolByName
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.schema import CreateSequence
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.interface import implementer
from zope.interface import Interface
from zope.sqlalchemy.datamanager import mark_changed
import logging


TRACKING_TABLE_NAME = 'opengever_upgrade_version'
TRACKING_TABLE_DEFINITION = (
    TRACKING_TABLE_NAME,
    Column('profileid', String(50), primary_key=True),
    Column('upgradeid', BigInteger, primary_key=True),
)

# Module global to keep a reference to the tracking table across several
# instances of SchemaMigration upgrade steps
_tracking_table = None

logger = logging.getLogger('opengever.upgrade')


class AbortUpgrade(Exception):
    """The upgrade had to be aborted for the reason specified in message."""


class ISchemaMigration(Interface):
    """Marker interface for upgrade steps which apply schema migrations to the
    SQL database and should therefore only be executed once per database.
    """


def get_operations(connection):
    """MySQL does not have transactional DDL, we might have to recover
    from partially executed migrations, thus we use IdempotentOperations.

    For all other DBMS (oracle and PostgreSQL) use alembic operations since
    they have transactional DDL and IdempotentOperations does not work
    there.
    """
    cache_name = '_migration_operations'
    if hasattr(connection, cache_name):
        return getattr(connection, cache_name)

    migration_context = MigrationContext.configure(connection)
    if connection.dialect.name == 'mysql':
        operations = IdempotentOperations(migration_context)
    else:
        operations = Operations(migration_context)

    setattr(connection, cache_name, operations)
    return operations


@decorator
def metadata_operation(f, *args, **kwargs):
    """Refresh metadata after executing an operation."""

    operations = args[0]
    result = f(*args, **kwargs)
    operations._refresh_metadata()
    return result


class IdempotentOperations(Operations):
    """Operations for MySQL - make alembic.operations tolerant to the same
    migration instruction being called multiple times.

    Works only for non-transactional DDL since it relies on a metadata
    instance to reflect about the database which seems not to see non-committed
    changes.

    This might happen when a DB-migration has been executed halfway but then
    fails. Since MYSQL does not support transaction aware schema changes we
    have to handle these partially executed migrations by ourself.

    XXX: once we drop MySQL support this class should be removed.

    """
    def __init__(self, migration_context, metadata):
        super(IdempotentOperations, self).__init__(migration_context)
        self.metadata = metadata

    def _get_table(self, table_name):
        return self.metadata.tables.get(table_name)

    def _get_column(self, table_name, column_name):
        table = self._get_table(table_name)
        if table is None:
            return None
        return table.columns.get(column_name)

    def _constraint_exists(self, name, table_name, type_):
        if type_ == 'unique':
            return self._has_index(name, table_name)
        else:
            return self._has_constraint(name, table_name)

    def _has_index(self, indexname, tablename):
        table = self.metadata.tables.get(tablename)
        for index in table.indexes:
            if index.name == indexname:
                return True
        return False

    def _has_constraint(self, name, tablename):
        table = self.metadata.tables.get(tablename)
        for constraint in table.constraints:
            if constraint.name == name:
                return True
        return False

    def _refresh_metadata(self):
        self.metadata.clear()
        self.metadata.reflect()

    @metadata_operation
    def drop_column(self, table_name, column_name, **kw):
        if self._get_column(table_name, column_name) is None:
            logger.log(logging.INFO,
                       "Skipping drop colum '{0}' of table '{1}', "
                       "column does not exist"
                       .format(column_name, table_name))
            return

        return super(IdempotentOperations, self).drop_column(
            table_name, column_name, **kw)

    @metadata_operation
    def add_column(self, table_name, column, schema=None):
        column_name = column.name
        if self._get_column(table_name, column_name) is not None:
            logger.log(logging.INFO,
                       "Skipping add colum '{0}' to table '{1}', "
                       "column does already exist"
                       .format(column_name, table_name))
            return

        return super(IdempotentOperations, self).add_column(
            table_name, column, schema)

    @metadata_operation
    def create_table(self, name, *columns, **kw):
        if self._get_table(name) is not None:
            logger.log(logging.INFO,
                       "Skipping create table '{0}', table does already exist"
                       .format(name))
            return

        return super(IdempotentOperations, self).create_table(
            name, *columns, **kw)

    @metadata_operation
    def drop_constraint(self, name, table_name, type_=None, schema=None):
        if not self._constraint_exists(name, table_name, type_):
            logger.log(logging.INFO,
                       "Skipping drop constraint '{0}' for table '{1}', "
                       "constraint does not exists."
                       .format(name, table_name))
            return

        super(IdempotentOperations, self).drop_constraint(
            name, table_name, type_=type_, schema=schema)

    @metadata_operation
    def create_unique_constraint(self, name, source, local_cols,
                                 schema=None, **kw):
        if self._has_index(name, source):
            logger.log(logging.INFO,
                       "Skipping create unique constraint '{0}' for table '{1}', "
                       "constraint already exists."
                       .format(name, source))
            return

        return super(IdempotentOperations, self).create_unique_constraint(
            name, source, local_cols, schema, **kw)

    @metadata_operation
    def batch_alter_table(self, *args, **kwargs):
        return super(IdempotentOperations, self).batch_alter_table(
            *args, **kwargs)

    @metadata_operation
    def rename_table(self, *args, **kwargs):
        return super(IdempotentOperations, self).rename_table(
            *args, **kwargs)

    @metadata_operation
    def alter_column(self, *args, **kwargs):
        return super(IdempotentOperations, self).alter_column(
            *args, **kwargs)

    @metadata_operation
    def create_primary_key(self, *args, **kwargs):
        return super(IdempotentOperations, self).create_primary_key(
            *args, **kwargs)

    @metadata_operation
    def create_foreign_key(self, *args, **kwargs):
        return super(IdempotentOperations, self).create_foreign_key(
            *args, **kwargs)

    @metadata_operation
    def create_check_constraint(self, *args, **kwargs):
        return super(IdempotentOperations, self).create_check_constraint(
            *args, **kwargs)

    @metadata_operation
    def drop_table(self, name, **kw):
        if self._get_table(name) is None:
            logger.log(logging.INFO,
                       "Skipping drop table '{0}', table no longer exist"
                       .format(name))
            return

        return super(IdempotentOperations, self).drop_table(name, **kw)

    @metadata_operation
    def create_index(self, name, table_name, columns, schema=None,
                     unique=False, quote=None, **kw):
        if self._has_index(name, table_name):
            logger.log(logging.INFO,
                       "Skipping create index '{0}' for table '{1}', "
                       "index already exists."
                       .format(name, table_name))
            return

        return super(IdempotentOperations, self).create_index(
            name, table_name, columns,
            schema=schema, unique=unique, quote=quote, **kw)

    @metadata_operation
    def drop_index(self, name, table_name=None, schema=None):
        if not self._has_index(name, table_name):
            logger.log(logging.INFO,
                       "Skipping drop index '{0}' for table '{1}', "
                       "index no longer exists."
                       .format(name, table_name))
            return

        return super(IdempotentOperations, self).drop_index(
            name, table_name=table_name, schema=schema)


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
        self.op.drop_constraint(self.name, self.source, type_='foreignkey')

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.op.create_foreign_key(self.name, self.source, self.referent,
                                   self.source_cols, self.referent_cols)
        return False


class SQLUpgradeStep(UpgradeStep):
    """Baseclass for upgrade steps that modify database content.

    This migration is run per plone site, if you want a migration that runs
    only once have a look at `SchemaMigration`.

    """
    def __call__(self):
        self._setup_db_connection()
        self.migrate()

    def migrate(self):
        raise NotImplementedError()

    def execute(self, statement):
        """Execute statement and make sure the datamanger sees the changes."""

        mark_changed(self.session)
        return self.connection.execute(statement)

    def _setup_db_connection(self):
        self.session = create_session()
        self.connection = self.session.connection()

    def has_multiple_admin_units(self):
        admin_unit_table = table("admin_units", column("unit_id"))
        query = self.session.query(admin_unit_table.c.unit_id)
        return query.count() > 1


@implementer(ISchemaMigration)
class SchemaMigration(SQLUpgradeStep):
    """Baseclass for database schema migrations.

    Maintains a tracking table to make sure that a schema migration is only
    run once.
    """

    def __call__(self):
        self._assert_configuration()
        self._setup_db_connection()
        self.migrate()
        mark_changed(self.session)

    @property
    def profileid(self):
        """The standard profile id is the base_profile provided by the upgrade
        step discovery of ftw.upgrade.
        Older migrations are overriding the `profileid` attribute.
        """
        return self.base_profile

    @property
    def upgradeid(self):
        """The `upgradeid` is based on the upgrade step's target version
        provided by ftw.upgrade's upgrade step discovery.

        Older migrations are overriding the `upgradeid` attribute.
        """
        return int(self.target_version)

    def refresh_metadata(self):
        self.metadata.clear()
        self.metadata.reflect()

    def get_foreign_key_name(self, table_name, column_name):
        table = self.metadata.tables.get(table_name)
        foreign_keys = table.columns.get(column_name).foreign_keys
        assert len(foreign_keys) == 1
        return foreign_keys.pop().name

    @property
    def supports_sequences(self):
        return self.op.impl.dialect.supports_sequences

    def ensure_sequence_exists(self, sequence_name):
        if not self.supports_sequences:
            return None
        if self.op.impl.dialect.has_sequence(self.connection, sequence_name):
            return False
        self.op.execute(CreateSequence(Sequence(sequence_name)))
        return True

    @property
    def is_oracle(self):
        # Could be 'oracle' or 'oracle+cx_oracle'
        return 'oracle' in self.dialect_name

    @property
    def is_postgres(self):
        return self.dialect_name == 'postgresql'

    @property
    def is_mysql(self):
        return self.dialect_name == 'mysql'

    def _assert_configuration(self):
        assert self.profileid is not None, 'configure a profileid'
        assert self.upgradeid is not None, 'configure an upgradeid'
        assert int(self.upgradeid) > 0, 'upgradeid must be > 0'
        assert len(self.profileid) < 50, 'profileid max length is 50 chars'

    def _setup_db_connection(self):
        super(SchemaMigration, self)._setup_db_connection()

        self.dialect_name = self.connection.dialect.name
        self.metadata = MetaData(self.connection)
        self.metadata.reflect()
        self.op = get_operations(self.connection)


class GeverUpgradeStepRecorder(UpgradeStepRecorder):
    """The upgrade step recorder is customized for GEVER in order to track
    SQL schema migrations in an SQL table, so that schema migrations are only
    executed once per cluster.

    The customization is responsible for the tracking table: it creates,
    updates and migrates the tracking table.
    """

    def is_installed(self, target_version):
        if self.is_marked_installed_in_sql(target_version):
            return True
        return super(GeverUpgradeStepRecorder, self).is_installed(target_version)

    def mark_as_installed(self, target_version):
        super(GeverUpgradeStepRecorder, self).mark_as_installed(target_version)
        self.mark_as_installed_in_sql(target_version)

    def is_marked_installed_in_sql(self, target_version):
        if not self.is_schema_migration(target_version):
            return False  # not a SchemaMigration, so its not tracked in SQL.

        self._setup_db_connection()
        tracking_record = self.session.query(self._get_tracking_table()).filter_by(
            profileid=self.profile,
            upgradeid=target_version).first()

        return tracking_record is not None

    def mark_as_installed_in_sql(self, target_version):
        if not self.is_schema_migration(target_version):
            return False  # we only track SchemaMigration upgrade steps in SQL

        if self.is_marked_installed_in_sql(target_version):
            return False  # Version is already marked as installed.

        self._setup_db_connection()
        mark_changed(self.session)
        self.session.execute(self._get_tracking_table().insert().values(
            profileid=self.profile,
            upgradeid=target_version))

    def is_schema_migration(self, target_version):
        portal_setup = getToolByName(self.portal, 'portal_setup')
        for info in portal_setup.listUpgrades(self.profile, show_old=True):
            if not isinstance(info, dict):
                # Upgrade step groups are nested in a list and they never
                # contain schema migrations.
                continue

            if info['dest'] == (target_version,):
                return ISchemaMigration.providedBy(info['step'].handler)

        return False

    @forever.memoize
    def _get_tracking_table(self):
        """Fetches the tracking table from the DB schema metadata if present,
        or creates it if necessary.
        """
        metadata = MetaData(self.connection)
        metadata.reflect()
        table = metadata.tables.get(TRACKING_TABLE_NAME)
        if table is not None:
            self._migrate_tracking_table(table)
            return table
        else:
            mark_changed(self.session)
            return self.operations.create_table(*TRACKING_TABLE_DEFINITION)

    def _migrate_tracking_table(self, table):
        """Verify tracking table state and apply migrations on the fly when necessary.
        We cannot do that in a schema migration because the migration mechanism relies
        on it - thus we might need to run other schema migrations before running the
        migration updating the table to the state the code expects.
        """
        if not table.columns.get('upgradeid').primary_key:
            # We need a primarykey over both columns (profileid and upgradeid) in order
            # to track / record each upgrade step for a profile; we used to only store
            # the newest version.
            mark_changed(self.session)
            for constraint in table.constraints:
                self.operations.drop_constraint(constraint.name,
                                                TRACKING_TABLE_NAME)
            self.operations.create_primary_key('opengever_upgrade_version_pkey',
                                               TRACKING_TABLE_NAME,
                                               ['profileid', 'upgradeid'])

    def _setup_db_connection(self):
        self.session = create_session()
        self.connection = self.session.connection()
        self.operations = get_operations(self.connection)
