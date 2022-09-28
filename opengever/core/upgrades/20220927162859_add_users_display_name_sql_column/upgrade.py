from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddUsersDisplayNameSQLColumn(SchemaMigration):
    """Add users.display_name SQL column.
    """

    def migrate(self):
        self.op.add_column(
            'users', Column('display_name', String(511), nullable=True)
        )
        # No need to pre-populate column as part of the upgrade,
        # since it will be populated by the next OGDS sync.
