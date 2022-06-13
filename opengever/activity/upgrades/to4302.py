from opengever.core.upgrade import SchemaMigration
from sqlalchemy import DateTime


class AlterActivityCreatedColumn(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4302

    def migrate(self):
        self.alter_created_column()

    def alter_created_column(self):
        self.op.alter_column(
            table_name='activities',
            column_name='created',
            type_=DateTime(timezone=True),
        )
