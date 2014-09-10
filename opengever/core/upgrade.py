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

    def refresh_medatata(self):
        self.metadata.clear()
        self.metadata.reflect()

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
        self.refresh_medatata()

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
        self.op = Operations(MigrationContext.configure(self.connection))
        self.metadata = MetaData(engine, reflect=True)
