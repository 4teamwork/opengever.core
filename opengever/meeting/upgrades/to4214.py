from datetime import datetime
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class ReplaceTimeFields(SchemaMigration):
    """Drop three date/time fields in favour of two dattime fields.
    It replaces the `date`, `start_time`, `end_time` column with two
    datetime fields (start & end)"""

    profileid = 'opengever.meeting'
    upgradeid = 4214

    def migrate(self):
        self.add_datetime_columns()

        if self.is_oracle:
            self.migrate_data_oracle()
        else:
            self.migrate_data()

        self.drop_date_and_time_columns()
        self.make_start_column_required()

    def add_datetime_columns(self):
        self.op.add_column(
            'meetings', Column('start', DateTime))
        self.op.add_column(
            'meetings', Column('end', DateTime))

    def migrate_data(self):
        meeting_table = table(
            "meetings",
            column("id"),
            column("date"),
            column("start_time"),
            column("end_time"),
            column("start"),
            column("end"),
        )

        meetings = self.connection.execute(meeting_table.select()).fetchall()
        for meeting in meetings:
            date = meeting.date
            start_time = meeting.start_time or datetime.min.time()
            end_time = meeting.end_time or datetime.min.time()

            start = datetime.combine(date, start_time)
            end = datetime.combine(date, end_time)

            self.execute(
                meeting_table.update()
                .values(start=start, end=end)
                .where(meeting_table.columns.id == meeting.id)
            )

    def migrate_data_oracle(self):
        """Because oracle does not support the Time datatype.
        We add a special handling to the 4200 upgradestep (AddMeetingTable)
        which creates Datetime fields instead of Time,
        therefore it's not possible to migrate date from the existing table.
        But we could presume, that there is not content created since then.
        """

        meeting_table = table("meetings", column("id"))
        meetings = self.connection.execute(meeting_table.select()).fetchall()
        assert len(meetings) == 0

    def drop_date_and_time_columns(self):
        self.op.drop_column('meetings', 'date')
        self.op.drop_column('meetings', 'start_time')
        self.op.drop_column('meetings', 'end_time')

    def make_start_column_required(self):
        self.op.alter_column('meetings', 'start', nullable=False,
                             existing_type=DateTime)
