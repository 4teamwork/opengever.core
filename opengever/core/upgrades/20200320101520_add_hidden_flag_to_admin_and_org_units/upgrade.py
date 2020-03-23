from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddHiddenFlagToAdminAndOrgUnits(SchemaMigration):
    """Add hidden flag to admin and org units.
    """

    def migrate(self):
        for tablename in ['admin_units', 'org_units']:
            self.add_column(tablename)
            self.insert_default_value(tablename)
            self.make_column_non_nullable(tablename)

    def add_column(self, tablename):
        self.op.add_column(
            tablename,
            Column('hidden', Boolean, default=False, nullable=True))

    def insert_default_value(self, tablename):
        _table = table(
            tablename,
            column("unit_id"),
            column("hidden"))

        self.connection.execute(
            _table.update().values(hidden=False))

    def make_column_non_nullable(self, tablename):
        self.op.alter_column(tablename, 'hidden',
                             existing_type=Boolean, nullable=False)
