from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddDecisionNrToProposal(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4621

    def migrate(self):
        self.add_decision_sequence_to_period()
        self.add_decision_number_to_agenda_item()

    def add_decision_sequence_to_period(self):
        self.op.add_column(
            'periods',
            Column('decision_sequence_number', Integer, nullable=True))

        periods_table = table(
            'periods',
            column('id'), column('decision_sequence_number'))
        self.execute(periods_table.update().values(decision_sequence_number=0))

        self.op.alter_column('periods', 'decision_sequence_number',
                             existing_type=Integer,
                             nullable=False)

    def add_decision_number_to_agenda_item(self):
        self.op.add_column(
            'agendaitems', Column('decision_number', Integer))
