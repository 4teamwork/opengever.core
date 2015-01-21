from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text


class AddProtocolsToMeetings(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4202

    def migrate(self):
        self.create_agenda_item_columns()
        self.create_meeting_columns()
        self.create_participants_secondary_table()

    def create_agenda_item_columns(self):
        self.op.add_column('agendaitems', Column('discussion', Text()))
        self.op.add_column('agendaitems', Column('decision', Text()))

    def create_meeting_columns(self):
        self.op.add_column(
            'meetings',
            Column('presidency_id', Integer, ForeignKey('members.id')))

        self.op.add_column(
            'meetings',
            Column('secretary_id', Integer, ForeignKey('members.id')))

        self.op.add_column('meetings', Column('other_participants', Text()))

    def create_participants_secondary_table(self):
        self.op.create_table(
            'meeting_participants',
            Column('meeting_id', Integer, ForeignKey('meetings.id')),
            Column('member_id', Integer, ForeignKey('members.id')))
