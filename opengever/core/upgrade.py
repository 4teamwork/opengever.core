from alembic.migration import MigrationContext
from alembic.operations import Operations
from BTrees.IIBTree import IITreeSet
from BTrees.OOBTree import OOTreeSet
from decorator import decorator
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import UpgradeStep
from ftw.upgrade.directory.recorder import UpgradeStepRecorder
from ftw.upgrade.helpers import update_security_for
from ftw.upgrade.utils import SavepointIterator
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from opengever.base.default_values import set_default_value
from opengever.base.model import create_session
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.base.utils import unrestrictedUuidToObject
from opengever.nightlyjobs.maintenance_jobs import MaintenanceJob
from opengever.nightlyjobs.maintenance_jobs import MaintenanceJobType
from opengever.nightlyjobs.maintenance_jobs import MaintenanceQueuesManager
from operator import itemgetter
from plone import api
from plone.memoize import forever
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from sqlalchemy import and_
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.schema import CreateSequence
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
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

    def get_index_names(self, table_name):
        if self.is_postgres:
            # SQLAlchemy < 2.0 doesn't support reflection of expression based
            # indexes. If we were to just use MetaData.indexes we would
            # therefore miss indexes like 'ix_groups_users_userid_lower'.
            # So we query the names ourselves from pg_indexes.
            query = (
                select([column('indexname')])
                .select_from(table('pg_indexes'))
                .where(
                    and_(
                        column('schemaname') == 'public',
                        column('tablename') == table_name))
                .order_by('indexname')
            )
            results = self.connection.execute(query).fetchall()
            return map(itemgetter(0), results)

        else:
            # Oracle
            #
            # XXX: Check whether this also works for expression based indexes
            # once we start testing og.core >= 2022.19.0 on Zug DEV.
            tbl = self.metadata.tables.get(table_name)
            if tbl is not None:
                return [idx.name for idx in tbl.indexes]

        return []

    def has_index(self, idx_name, table_name):
        index_names = self.get_index_names(table_name)
        return idx_name in index_names

    def create_index_if_not_exists(self, idx_name, table_name, idx_columns):
        if not self.has_index(idx_name, table_name):
            logger.info('Creating index {}.{}'.format(table_name, idx_name))
            self.op.create_index(idx_name, table_name, idx_columns)
        else:
            logger.info('Index {}.{} already exists, skipping creation.'.format(
                table_name, idx_name))

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


class MaintenanceJobContextManagerMixin(object):

    queue_type = None

    def __init__(self, commit_to_solr=False):
        self.commit_to_solr = commit_to_solr
        self.queue_manager = MaintenanceQueuesManager(api.portal.get())
        self.check_preconditions()

    def __enter__(self):
        key, self.queue = self.queue_manager.add_queue(
            self.job_type,
            queue_type=self.queue_type,
            commit_batch_size=1000,
            commit_to_solr=self.commit_to_solr)
        return self

    def add_by_obj(self, obj):
        self._add_by_key(self.obj_to_key(obj))

    def _add_by_key(self, key):
        self.queue_manager.add_job(MaintenanceJob(self.job_type, key))

    def obj_to_key(self, obj):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.queue) == 0:
            self.queue_manager.remove_queue(self.job_type)

    def check_preconditions(self):
        pass

    @property
    def job_type(self):
        raise NotImplementedError()


class IntIdMaintenanceJobContextManagerMixin(MaintenanceJobContextManagerMixin):
    """Storing IntIds in the queue is efficient memory-wise but the object is
    needed to get its IntId, making the upgrade step itself slower and less
    memory efficient.
    """
    queue_type = IITreeSet

    def __init__(self, commit_to_solr=False):
        super(IntIdMaintenanceJobContextManagerMixin, self).__init__(commit_to_solr)
        self.intids = getUtility(IIntIds)

    def obj_to_key(self, obj):
        int_id = self.intids.queryId(obj)
        if not int_id:
            int_id = self.intids.register(obj)
        return int_id

    @staticmethod
    def key_to_obj(key):
        intids = getUtility(IIntIds)
        return intids.queryObject(key)


class UIDMaintenanceJobContextManagerMixin(MaintenanceJobContextManagerMixin):
    """Storing UUIDs in the queue uses around 4 times as more memory than
    the IntID, but the UUID can be obtained from the brain, making the upgrade
    step itself very fast with a low memory footprint.
    """

    queue_type = OOTreeSet

    def obj_to_key(self, obj):
        return IUUID(obj)

    @staticmethod
    def key_to_obj(key):
        return unrestrictedUuidToObject(key)

    def add_by_brain(self, brain):
        self._add_by_key(brain.UID)


class NightlyIndexer(UIDMaintenanceJobContextManagerMixin):

    def __init__(self, idxs, index_in_solr_only=False):
        self.idxs = idxs
        self.index_in_solr_only = index_in_solr_only
        super(NightlyIndexer, self).__init__(index_in_solr_only)

    @property
    def job_type(self):
        if self.index_in_solr_only:
            function_name = self.index_in_solr.__name__
        else:
            function_name = self.index_in_catalog.__name__

        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         function_name))
        return MaintenanceJobType(function_dotted_name, idxs=tuple(self.idxs))

    def check_preconditions(self):
        if self.index_in_solr_only and 'SearchableText' in self.idxs:
            raise ValueError(
                "Reindexing SearchableText in solr only is not supported")

    @classmethod
    def index_in_catalog(cls, key, idxs):
        obj = cls.key_to_obj(key)
        if obj:
            obj.reindexObject(idxs=idxs)

    @classmethod
    def index_in_solr(cls, key, idxs):
        obj = cls.key_to_obj(key)
        if obj:
            manager = getUtility(ISolrConnectionManager)
            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add(idxs)


class DefaultValuePersister(UIDMaintenanceJobContextManagerMixin):

    def __init__(self, fields):
        self.fields = sorted(fields)
        super(DefaultValuePersister, self).__init__()

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.persist_fields.__name__))
        fields_tuples = tuple((field.interface.__identifier__, field.getName())
                              for field in self.fields)
        return MaintenanceJobType(function_dotted_name,
                                  fields_tuples=fields_tuples)

    @classmethod
    def persist_fields(cls, key, fields_tuples):
        obj = cls.key_to_obj(key)
        if not obj:
            return
        for interfacename, fieldname in fields_tuples:
            try:
                interface = resolve(interfacename)
            except ImportError:
                return
            field = interface.get(fieldname)
            if not field:
                return
            set_default_value(obj, obj.aq_parent, field)


class NightlyWorkflowSecurityUpdater(IntIdMaintenanceJobContextManagerMixin, WorkflowSecurityUpdater):

    def __init__(self, reindex_security):
        WorkflowSecurityUpdater.__init__(self)
        self.reindex_security = reindex_security
        super(NightlyWorkflowSecurityUpdater, self).__init__()

    def update(self, changed_workflows, savepoints=1000):
        types = self.get_suspected_types(changed_workflows)
        objects = SavepointIterator.build(self.lookup_objects(types), savepoints)
        for obj in objects:
            if self.obj_has_workflow(obj, changed_workflows):
                self.add_by_obj(obj)

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.update_security_for.__name__))
        return MaintenanceJobType(function_dotted_name,
                                  reindex_security=self.reindex_security)

    @classmethod
    def update_security_for(cls, key, reindex_security):
        obj = cls.key_to_obj(key)

        if obj is None:
            logger.warn(
                'NightlyWorkflowSecurityUpdater: Failed to resolve key %r to '
                'object, skipping' % key)
            return

        update_security_for(obj, reindex_security)


# For 0220127165920_migrate_dossier_comments
COMMENTS_KEY = 'opengever.dossier.behaviors.dossier.IDossier.comments'


class DossierCommentsMigrator(UIDMaintenanceJobContextManagerMixin):

    def __init__(self):
        super(DossierCommentsMigrator, self).__init__()

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.migrate_comments.__name__))

        return MaintenanceJobType(function_dotted_name)

    @classmethod
    def migrate_comments(cls, key):
        dossier = cls.key_to_obj(key)
        if not dossier:
            return
        annotations = IAnnotations(dossier)
        if COMMENTS_KEY in annotations and annotations[COMMENTS_KEY]:
            response = Response(COMMENT_RESPONSE_TYPE)
            response.text = annotations[COMMENTS_KEY]
            response.creator = None
            IResponseContainer(dossier).add(response)
            del annotations[COMMENTS_KEY]


class NightlyDossierCommentIndexer(NightlyIndexer):

    def check_preconditions(self):
        # the default NightlyIndexer avoid reindexing the SearchableText only
        # in solr, but for our case where only dossiers needs reindexing
        # it's ok.
        pass

    @classmethod
    def index_in_solr(cls, key, idxs):
        obj = cls.key_to_obj(key)
        if obj and len(IResponseContainer(obj)) > 0:
            manager = getUtility(ISolrConnectionManager)
            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add(idxs)


class FixGhostChecksums(UIDMaintenanceJobContextManagerMixin):
    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.fix_ghost_checksum.__name__))

        return MaintenanceJobType(function_dotted_name)

    @classmethod
    def fix_ghost_checksum(cls, key):
        obj = cls.key_to_obj(key)
        if not obj:
            return

        doc = IBumblebeeDocument(obj)
        if doc.is_convertable():
            # Checksums of already convertable documents are not affected
            return

        if not doc.get_checksum():
            # Non convertable documents should have no checksum.
            return

        # We need to update the checksum for non convertable documents
        # still having a checksum.
        doc.update_checksum()
        obj.reindexObject(idxs=["getId", "bumblebee_checksum"])
