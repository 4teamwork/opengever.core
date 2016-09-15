from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer


class AddFormerContactIdColumn(SchemaMigration):
    """Add former contact id column.
    """

    def migrate(self):
        self.op.add_column(
            'contacts',
            Column('former_contact_id', Integer, nullable=True, unique=True))
