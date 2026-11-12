# -*- coding: utf-8 -*-
from datetime import datetime
from ftw.testing import freeze
from opengever.exportng.tests.layer import EXPORTNG_DB_INTEGRATION_TESTING
import pytz


SYSTEM_COLUMNS = ('_modified_at', '_deleted', '_imported_at', '_objaddress')

SYNC_1 = datetime(2026, 5, 20, 14, 30, tzinfo=pytz.utc)
MODIFIED = datetime(2026, 5, 21, 18, 0, tzinfo=pytz.utc)
SYNC_2 = datetime(2026, 5, 22, 8, 0, tzinfo=pytz.utc)
SYNC_3 = datetime(2026, 5, 23, 8, 0, tzinfo=pytz.utc)


class SyncerTestMixin(object):
    """Generic tests for subclasses of `CatalogSyncer`.

    Combine with `IntegrationTestCase` and implement the hooks below:

    - `syncer_class_name`: name of the syncer class in `opengever.exportng.catalog`.
    - `expected_rows()`: `{objexternalkey: {column: value}}` for every object
      that has to be exported. Contains all mapped columns, without the
      system columns (`_modified_at`, `_deleted`, ...).
    - `object_to_modify()` / `modify(obj)`: modify an exported object so that
      it is reindexed, `modified_columns` are the resulting changed columns.
    - `object_to_delete()`: an exported object that may be deleted.

    The sync is always run with a new syncer instance, so no state is shared
    between consecutive syncs.
    """

    layer = EXPORTNG_DB_INTEGRATION_TESTING

    syncer_class_name = None
    modified_columns = {}

    def setUp(self):
        super(SyncerTestMixin, self).setUp()
        # Import lazily: the db module reads the DSN at import time, which is
        # set by the layer.
        from opengever.exportng.db import metadata
        from opengever.exportng.sync import Syncer
        metadata.drop_all()
        metadata.clear()
        Syncer().create_tables()
        self.metadata = metadata
        self.login(self.manager)

    # Hooks

    def expected_rows(self):
        raise NotImplementedError

    def object_to_modify(self):
        raise NotImplementedError

    def modify(self, obj):
        raise NotImplementedError

    def object_to_delete(self):
        raise NotImplementedError

    def delete(self, obj):
        from plone import api
        api.content.delete(obj=obj, check_linkintegrity=False)

    # Helpers

    def new_syncer(self):
        from opengever.exportng import catalog
        return getattr(catalog, self.syncer_class_name)()

    def sync(self, at=None):
        if at is None:
            self.new_syncer().sync()
        else:
            with freeze(at):
                self.new_syncer().sync()

    def fetch_rows(self):
        """Returns all rows (including deleted ones) by objexternalkey."""
        from opengever.exportng.db import engine
        table = self.metadata.tables[self.new_syncer().table]
        with engine.connect() as conn:
            return {row.objexternalkey: dict(row.items())
                    for row in conn.execute(table.select()).fetchall()}

    def data_of(self, row):
        return {k: v for k, v in row.items() if k not in SYSTEM_COLUMNS}

    # Tests

    def test_initial_sync_exports_all_objects(self):
        self.assertEqual({}, self.fetch_rows())

        self.sync()

        rows = self.fetch_rows()
        self.assertItemsEqual(self.expected_rows().keys(), rows.keys())
        for key, row in rows.items():
            self.assertFalse(row['_deleted'], key)
            self.assertIsNotNone(row['_modified_at'], key)
            self.assertIsNone(row['_imported_at'], key)
            self.assertIsNone(row['_objaddress'], key)

    def test_all_attributes_are_exported_as_expected(self):
        self.sync()

        rows = self.fetch_rows()
        for key, expected in self.expected_rows().items():
            self.assertEqual(expected, self.data_of(rows[key]), key)

    def test_all_mapped_columns_are_covered_by_expectations(self):
        columns = set(attr.col_name for attr in self.new_syncer().serializer.mapping)
        for key, expected in self.expected_rows().items():
            self.assertEqual(columns, set(expected.keys()), key)

    def test_consecutive_sync_without_changes_changes_nothing(self):
        self.sync(SYNC_1)
        before = self.fetch_rows()

        self.sync(SYNC_2)

        self.assertEqual(before, self.fetch_rows())

    def test_consecutive_sync_updates_only_modified_objects(self):
        self.sync(SYNC_1)
        before = self.fetch_rows()

        obj = self.object_to_modify()
        key = obj.UID()
        with freeze(MODIFIED):
            self.modify(obj)
        self.sync(SYNC_2)

        after = self.fetch_rows()
        self.assertItemsEqual(before.keys(), after.keys())
        for other in set(before) - set([key]):
            self.assertEqual(before[other], after[other], other)

        expected = dict(self.data_of(before[key]), **self.modified_columns)
        self.assertEqual(expected, self.data_of(after[key]))
        self.assertGreater(after[key]['_modified_at'], before[key]['_modified_at'])
        self.assertFalse(after[key]['_deleted'])

        # The modification is not exported again
        self.sync(SYNC_3)
        self.assertEqual(after, self.fetch_rows())

    def test_deleted_objects_are_marked_as_deleted(self):
        self.sync(SYNC_1)
        before = self.fetch_rows()

        obj = self.object_to_delete()
        key = obj.UID()
        self.delete(obj)
        self.sync(SYNC_2)

        after = self.fetch_rows()
        # Rows are kept, only flagged
        self.assertItemsEqual(before.keys(), after.keys())
        self.assertTrue(after[key]['_deleted'])
        self.assertEqual(self.data_of(before[key]), self.data_of(after[key]))
        for other in set(before) - set([key]):
            self.assertEqual(before[other], after[other], other)

        # Consecutive syncs keep it deleted
        self.sync(SYNC_3)
        self.assertEqual(after, self.fetch_rows())
