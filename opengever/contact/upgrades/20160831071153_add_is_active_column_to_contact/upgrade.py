from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddIsActiveColumnToContact(SchemaMigration):
    """Add is active column to contact.
    """

    def migrate(self):
        for tablename in ['contacts', 'archived_contacts']:
            self.add_column(tablename)
            self.insert_default_value(tablename)
            self.make_column_non_nullable(tablename)

    def add_column(self, tablename):
        self.op.add_column(
            tablename,
            Column('is_active', Boolean, default=True, nullable=True))

    def insert_default_value(self, tablename):
        contact_table = table(
            tablename,
            column("id"),
            column("is_active"))

        self.connection.execute(
            contact_table.update().values(is_active=True))

    def make_column_non_nullable(self, tablename):
        self.op.alter_column(tablename, 'is_active',
                             existing_type=Boolean, nullable=False)
