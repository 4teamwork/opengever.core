from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddTitleColumnToOGDSUserModel(SchemaMigration):
    """Add title column to OGDS user model.
    """

    def migrate(self):
        self.op.add_column('users', Column('title', String(255)))
