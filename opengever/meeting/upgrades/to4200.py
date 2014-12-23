from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Time
from sqlalchemy.schema import Sequence


class AddMeetingTable(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4200

    def migrate(self):
        self.create_meeting_table()
        self.create_agenda_item_table()
        self.add_proposal_columns()
        self.add_committee_columns()

    def create_meeting_table(self):
        self.op.create_table(
            'meetings',
            Column("id", Integer, Sequence("meeting_id_seq"), primary_key=True),
            Column("committee_id", Integer, ForeignKey('committees.id'), nullable=False),
            Column("location", String(256)),
            Column("date", Date, nullable=False),
            Column("start_time", Time),
            Column("end_time", Time),
            Column("workflow_state", String(256), nullable=False, default='pending')
        )

    def create_agenda_item_table(self):
        self.op.create_table(
            'agendaitems',
            Column("id", Integer, Sequence("agendaitems_id_seq"), primary_key=True),
            Column("agenda_item_id", Integer, ForeignKey('meetings.id'), nullable=False),
            Column("proposal_id", Integer, ForeignKey('proposals.id')),
            Column("title", Text),
            Column("sort_order", Integer, nullable=False, default=0),
        )

    def add_proposal_columns(self):
        self.op.add_column('proposal',
                           Column('submitted_physical_path', String(256)))

    def add_committee_columns(self):
        self.op.add_column('committees',
                           Column('physical_path', String(256), nullable=False))
