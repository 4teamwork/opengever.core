from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date


class AddLastLoginColumnToUsers(SchemaMigration):
    """Add last_login column to users.
    """

    def migrate(self):
        self.op.add_column(
            'users', Column('last_login', Date, index=True, nullable=True)
        )
