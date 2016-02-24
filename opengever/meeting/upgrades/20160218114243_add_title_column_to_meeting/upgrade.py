from opengever.core.upgrade import SchemaMigration
from plone import api
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


meeting_table = table("meetings",
                      column("id"),
                      column("title"),
                      column("location"),
                      column("start_datetime"))


class AddTitleColumnToMeeting(SchemaMigration):
    """Add title column to meeting.
    """

    def migrate(self):
        self.add_column()
        self.migrate_data()
        self.make_column_non_nullable()

    def add_column(self):
        self.op.add_column(
            'meetings',
            Column('title', Text, nullable=True))

    def migrate_data(self):
        for meeting in self.execute(meeting_table.select()):
            self._set_title(meeting)

    def _set_title(self, meeting):
        self.execute(meeting_table
                     .update()
                     .where(meeting_table.c.id == meeting.id)
                     .values(title=self._generate_title(meeting)))

    def _generate_title(self, meeting):
        date = api.portal.get_localized_time(datetime=meeting.start_datetime)
        if meeting.location:
            return u"{}, {}".format(meeting.location, date)
        return date

    def make_column_non_nullable(self):
        self.op.alter_column('meetings', 'title',
                             existing_type=Text, nullable=False)
