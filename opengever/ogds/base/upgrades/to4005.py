from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddAbbreviationColumn(SchemaMigration):

    profileid = 'opengever.ogds.base'
    upgradeid = 4005

    def migrate(self):
        self.add_abbreviation_column()
        self.insert_default_value()
        self.make_abbreviation_column_required()

    def add_abbreviation_column(self):
        self.op.add_column(
            'admin_units',
            Column('abbreviation', String(50)))

        self.refresh_metadata()

    def insert_default_value(self):
        """Insert admin_units label as default value."""

        admin_units_table = self.metadata.tables.get('admin_units')
        units = self.connection.execute(
            admin_units_table.select()).fetchall()

        for row in units:
            self.execute(admin_units_table.update()
                         .values(abbreviation=row.title)
                         .where(admin_units_table.c.unit_id == row.unit_id))

    def make_abbreviation_column_required(self):
        self.op.alter_column('admin_units', 'abbreviation',
                             nullable=False, existing_type=String(50))
