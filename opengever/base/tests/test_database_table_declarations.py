from opengever.activity.model import tables as activity_tables
from opengever.base.model import Base
from opengever.globalindex.model import tables as globalindex_tables
from opengever.meeting.model import tables as meeting_tables
from unittest2 import TestCase


class TestDatabaseTableDeclarations(TestCase):
    """Test that tables in metadata are in sync with manual table definitions.

    When this test fails it most likely means that you defined new database
    model classes or secondary tables but forgot to add them to the manual
    table list in its corresponding model package.

    The manual table list is necessary for certain upgrade steps to work
    correctly.

    """
    def test_package_table_definitions_are_correct(self):
        expected_tables = meeting_tables + activity_tables + globalindex_tables
        self.assertItemsEqual(expected_tables, Base.metadata.tables.keys())
