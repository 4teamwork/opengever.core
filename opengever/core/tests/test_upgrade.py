from alembic.migration import MigrationContext
from opengever.core.upgrade import IdempotentOperations
from opengever.core.upgrade import NightlyIndexer
from opengever.nightlyjobs.runner import NightlyJobRunner
from opengever.testing import index_data_for
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine.reflection import Inspector
from unittest import TestCase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestIdempotentOperations(TestCase):
    """Test database migration utilities.

    Unfortunately not all operations can be tested with an SQLite database
    since not all ALTER TABLE operations are supported, see
    http://www.sqlite.org/lang_altertable.html.

    Currenlty these untested operations are:
    - IdempotentOperations. drop_column
    - DeactivatedFKConstraint

    """
    def setUp(self):
        self.connection = create_engine('sqlite:///:memory:').connect()
        self.metadata = MetaData(self.connection)
        self.table = Table('thingy', self.metadata,
                           Column('thingy_id', Integer, primary_key=True))
        self.metadata.create_all()

        self.migration_context = MigrationContext.configure(self.connection)
        self.op = IdempotentOperations(self.migration_context, self.metadata)
        self.inspector = Inspector(self.connection)

    def tearDown(self):
        self.metadata.drop_all()
        self.connection.close()

    def refresh_metadata(self):
        self.metadata.clear()
        self.metadata.reflect()

    def test_add_column_works_with_valid_preconditions(self):
        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

        self.op.add_column('thingy', Column('foo', String))
        self.refresh_metadata()

        self.assertEqual(['thingy_id', 'foo'],
                         self.metadata.tables['thingy'].columns.keys())

    def test_add_column_skips_add_when_column_name_already_exists(self):
        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

        self.op.add_column('thingy', Column('thingy_id', String))
        self.refresh_metadata()

        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

    def test_create_tables_skips_create_when_table_already_exists(self):
        self.assertEqual(['thingy'], self.metadata.tables.keys())

        self.op.create_table('thingy')
        self.refresh_metadata()
        self.assertEqual(['thingy'], self.metadata.tables.keys())

    def test_create_table_works_with_valid_preconditions(self):
        self.assertEqual(['thingy'], self.metadata.tables.keys())
        self.op.create_table('xuq', Column('foo', Integer, primary_key=True))
        self.refresh_metadata()
        self.assertEqual(['thingy', 'xuq'], self.metadata.tables.keys())


class TestNightlyIndexer(SolrIntegrationTestCase):

    def run_nightly_jobs(self):
        runner = NightlyJobRunner(force_execution=True)
        runner.execute_pending_jobs()
        self.commit_solr()

    def assert_catalog_data(self, obj, idx, value):
        catalog_data = index_data_for(obj)
        self.assertEqual(value, catalog_data.get(idx))

    def assert_solr_data(self, obj, idx, value):
        solr_data = solr_data_for(obj)
        self.assertEqual(value, solr_data.get(idx))

    def assert_solr_and_catalog_data(self, obj, idx, value):
        self.assert_solr_data(obj, idx, value)
        self.assert_catalog_data(obj, idx, value)

    def test_nightly_indexer_indexes_only_passed_indexes(self):
        intids = getUtility(IIntIds)
        self.login(self.manager)
        old_creator = self.dossier.Creator()
        new_creator = "New creator"
        self.dossier.creators = (new_creator,)

        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title", "Creator"]) as indexer:
            indexer.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", new_creator)

    def test_nightly_solr_only_indexer(self):
        intids = getUtility(IIntIds)
        self.login(self.manager)
        old_creator = self.dossier.Creator()
        new_creator = "New creator"
        self.dossier.creators = (new_creator,)

        with NightlyIndexer(idxs=["Title"], index_in_solr_only=True) as indexer:
            indexer.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title", "Creator"], index_in_solr_only=True) as indexer:
            indexer.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()
        self.assert_solr_data(self.dossier, "Creator", new_creator)
        self.assert_catalog_data(self.dossier, "Creator", old_creator)

    def test_nightly_indexer_handles_multiple_jobs(self):
        intids = getUtility(IIntIds)
        self.login(self.manager)
        self.dossier.title = "New dossier title"
        self.empty_dossier.title = "New empty dossier title"
        self.subdossier.title = "New subdossier title"

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_intid(intids.getId(self.dossier))
            indexer.add_by_intid(intids.getId(self.subdossier))

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_intid(intids.getId(self.empty_dossier))

        self.run_nightly_jobs()
        self.assert_solr_data(self.dossier, "Title", "New dossier title")
        self.assert_solr_data(self.subdossier, "Title", "New subdossier title")
        self.assert_solr_data(self.empty_dossier, "Title", "New empty dossier title")
        self.assert_catalog_data(
            self.dossier, "Title", ["new", "dossier", "title"])
        self.assert_catalog_data(
            self.subdossier, "Title", ["new", "subdossier", "title"])
        self.assert_catalog_data(
            self.empty_dossier, "Title", ["new", "empty", "dossier", "title"])

    def test_trying_to_reindex_searchable_text_in_solr_raises(self):
        with self.assertRaises(ValueError) as exc:
            NightlyIndexer(idxs=["Title", "SearchableText"],
                           index_in_solr_only=True)
        self.assertEqual(
            'Reindexing SearchableText in solr only is not supported',
            exc.exception.message)
