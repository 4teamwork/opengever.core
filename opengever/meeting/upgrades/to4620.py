from opengever.base.date_time import utcnow_tz_aware
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddModifiedTimestampToMeeting(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4620

    def migrate(self):
        self.add_modified_column()
        self.insert_default_modified()
        self.make_modified_non_nullable()

    def add_modified_column(self):
        self.op.add_column(
            'meetings', Column('modified', DateTime(timezone=True),
                               nullable=True))

    def insert_default_modified(self):
        """Insert time of migration as last modified timestamp."""

        meeting_table = table(
            'meetings',
            column('id'),
            column('modified'),
        )

        self.execute(meeting_table.update().values(modified=utcnow_tz_aware()))

    def make_modified_non_nullable(self):
        self.op.alter_column('meetings', 'modified',
                             existing_type=DateTime(timezone=True),
                             nullable=False)
