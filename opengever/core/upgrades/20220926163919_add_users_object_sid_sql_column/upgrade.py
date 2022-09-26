from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddUsersObjectSidSQLColumn(SchemaMigration):
    """Add users.object_sid SQL column.
    """

    def migrate(self):
        # No need to pre-populate the column during the upgrade, since this
        # will be done during the next OGDS sync.
        self.op.add_column(
            'users', Column('object_sid', String(255), nullable=True)
        )
