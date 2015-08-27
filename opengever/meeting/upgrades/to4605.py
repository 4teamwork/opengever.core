from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class LinkMeetingToDossier(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4605

    def migrate(self):
        # This upgrade runs only when no content has been created.
        # This assumption holds because this will be the first "productive"
        # release of opengever.meeting.

        meeting_table = table("meetings", column("id"))
        meetings = self.connection.execute(meeting_table.select()).fetchall()
        assert len(meetings) == 0, "runs only for empty meeting-tables"

        self.add_dossier_columns()

    def add_dossier_columns(self):
        self.op.add_column('meetings',
                           Column('dossier_admin_unit_id', String(30),
                                  nullable=False))
        self.op.add_column('meetings',
                           Column('dossier_int_id', Integer, nullable=False))
