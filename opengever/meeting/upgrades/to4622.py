from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddMeetingNumber(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4622

    def migrate(self):
        self.add_meeting_sequence_to_period()
        self.add_meeting_number_to_meeting()

    def add_meeting_sequence_to_period(self):
        self.op.add_column(
            'periods',
            Column('meeting_sequence_number', Integer, nullable=True))

        periods_table = table(
            'periods',
            column('id'), column('meeting_sequence_number'))
        self.execute(periods_table.update().values(meeting_sequence_number=0))

        self.op.alter_column('periods', 'meeting_sequence_number',
                             existing_type=Integer,
                             nullable=False)

    def add_meeting_number_to_meeting(self):
        self.op.add_column(
            'meetings', Column('meeting_number', Integer))
