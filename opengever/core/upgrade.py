from alembic.migration import MigrationContext
from alembic.operations import Operations
from BTrees.IIBTree import IITreeSet
from BTrees.OOBTree import OOTreeSet
from decorator import decorator
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.mail.utils import get_attachments
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
    """Create a memoized Alembic 'Operations' instance.
    """
    cache_name = '_migration_operations'
    if hasattr(connection, cache_name):
        return getattr(connection, cache_name)

    migration_context = MigrationContext.configure(connection)
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
        if self.is_oracle:
            query = "SELECT * from all_objects WHERE object_name='{}'".format(idx_name)
            if len(self.connection.execute(query).fetchall()) > 0:
                return True
            return False

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

    def add_by_solr_document(self, doc):
        self._add_by_key(doc.get('UID'))


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


class NightlyMailAttachmentInfoUpdater(UIDMaintenanceJobContextManagerMixin):

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.update_attachment_infos.__name__))

        return MaintenanceJobType(function_dotted_name)

    @classmethod
    def update_attachment_infos(cls, key):
        mail = cls.key_to_obj(key)

        if not mail:
            return

        pos = itemgetter('position')

        existing_attachments = sorted(mail.attachment_infos, key=pos)
        updated_attachments = sorted(get_attachments(mail.msg), key=pos)

        if not list(map(pos, existing_attachments)) == list(map(pos, updated_attachments)):
            logger.warn(
                'NightlyMailAttachmentInfoUpdater: Failed to update '
                'attachments for mail %r' % mail)
            return

        for existing, updated in zip(existing_attachments, updated_attachments):
            assert existing['position'] == updated['position']
            assert existing['size'] == updated['size']
            mail._modify_attachment_info(**updated)
