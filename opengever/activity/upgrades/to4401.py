from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean


class RenameActivityAvoidReservedNames(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4401

    def migrate(self):
        self.rename_read_column()

    def rename_read_column(self):
        self.op.alter_column('notifications', 'read',
                             new_column_name='is_read',
                             existing_type=Boolean, existing_nullable=False)
