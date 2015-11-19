from datetime import date
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddPeriods(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4618

    def migrate(self):
        self.create_periods_table()
        self.create_default_periods_for_committees()

    def create_periods_table(self):
        self.periods_table = self.op.create_table(
            'periods',
            Column('id', Integer, primary_key=True),
            Column('committee_id', Integer,
                   ForeignKey('committees.id'), nullable=False),
            Column("workflow_state", String(255), nullable=False,
                   default='active'),
            Column('title', String(256), nullable=False),
            Column('date_from', Date),
            Column('date_to', Date),
        )

    def create_default_periods_for_committees(self):
        self.committees_table = table("committees", column("id"))
        self.date = date.today()
        self.end_of_year = date(self.date.year, 12, 31)

        for committee in self.connection.execute(
                self.committees_table.select()).fetchall():
            self.create_initial_period(committee)

    def create_initial_period(self, committee):
        self.execute(self.periods_table.insert().values(
            committee_id=committee.id,
            title=self.date.strftime('%Y').decode(),
            date_from=self.date,
            date_to=self.end_of_year))
