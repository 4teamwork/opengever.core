from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddCountryFieldToAddresses(SchemaMigration):
    """Add country field to addresses.
    """

    def migrate(self):
        self.op.add_column('addresses', Column('country', String(255)))
        self.op.add_column('archived_addresses', Column('country', String(255)))
