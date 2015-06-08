from opengever.core.upgrade import SchemaMigration
from sqlalchemy import DateTime
from sqlalchemy import String


class RenameMeetingAvoidReservedNames(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4400

    def migrate(self):
        self.rename_start_column()
        self.rename_end_column()
        self.rename_number_column()

    def rename_start_column(self):
        self.op.alter_column('meetings', 'start',
                             new_column_name='start_datetime',
                             existing_type=DateTime, existing_nullable=False)

    def rename_end_column(self):
        self.op.alter_column('meetings', 'end',
                             new_column_name='end_datetime',
                             existing_type=DateTime, existing_nullable=True)

    def rename_number_column(self):
        self.op.alter_column('agendaitems', 'number',
                             new_column_name='item_number',
                             existing_type=String(16), existing_nullable=True)
