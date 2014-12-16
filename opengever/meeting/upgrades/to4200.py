from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.schema import Sequence


class AddMeetingTable(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4200

    def migrate(self):
        self.create_meeting_table()

    def create_meeting_table(self):
        self.op.create_table(
            'meetings',
            Column("id", Integer, Sequence("meeting_id_seq"), primary_key=True),
            Column("committee_id", Integer, ForeignKey('committees.id'), nullable=False),
            Column("location", String(256)),
            Column("date", Date, nullable=False),
            Column("start_time", Time),
            Column("end_time", Time),
        )
