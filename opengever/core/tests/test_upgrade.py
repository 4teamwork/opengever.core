from alembic.migration import MigrationContext
from opengever.core.upgrade import IdempotentOperations
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine.reflection import Inspector
from unittest import TestCase


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
        self.op = IdempotentOperations(self.migration_context, self)
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
