from opengever.core.upgrade import SchemaMigration
from sqlalchemy import DateTime


class AlterMeetingDatetimeColumns(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4613

    def migrate(self):
        self.alter_meeting_columns()

    def alter_meeting_columns(self):
        self.op.alter_column(
            table_name='meetings',
            column_name='start_datetime',
            existing_nullable=False,
            type_=DateTime(timezone=True),
        )
        self.op.alter_column(
            table_name='meetings',
            column_name='end_datetime',
            existing_nullable=True,
            type_=DateTime(timezone=True),
        )
