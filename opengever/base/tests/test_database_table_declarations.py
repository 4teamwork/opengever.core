from opengever.activity.model import tables as activity_tables
from opengever.base.model import Base
from opengever.base.model import tables as base_tables
from opengever.contact.models import tables as contact_tables
from opengever.globalindex.model import tables as globalindex_tables
from opengever.locking.model import tables as lock_tables
from opengever.meeting.model import tables as meeting_tables
from unittest import TestCase


class TestDatabaseTableDeclarations(TestCase):
    """Test that tables in metadata are in sync with manual table definitions.

    When this test fails it most likely means that you defined new database
    model classes or secondary tables but forgot to add them to the manual
    table list in its corresponding model package.

    The manual table list is necessary for certain upgrade steps to work
    correctly.

    """
    def test_package_table_definitions_are_correct(self):
        expected_tables = (
            meeting_tables
            + activity_tables
            + globalindex_tables
            + lock_tables
            + contact_tables
            + base_tables
        )
        self.assertItemsEqual(expected_tables, Base.metadata.tables.keys())
