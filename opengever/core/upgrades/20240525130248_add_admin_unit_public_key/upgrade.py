from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddAdminUnitPublicKey(SchemaMigration):
    """Add new column public_key to admin_units table.
    """

    def migrate(self):
        self.op.add_column(
            'admin_units', Column('public_key', String(44), nullable=True)
        )
