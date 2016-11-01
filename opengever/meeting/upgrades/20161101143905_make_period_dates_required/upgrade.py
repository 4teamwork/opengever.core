from datetime import date
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Date
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class MakePeriodDatesRequired(SchemaMigration):
    """Make period dates required.
    """

    periods_table = table(
        'periods',
        column('id'),
        column('date_from'),
        column('date_to'),
    )

    def migrate(self):
        self.insert_default_period_start_end_date()
        self.make_period_date_columns_non_nullable()

    def insert_default_period_start_end_date(self):
        today = date.today()
        for period in self.connection.execute(
                self.periods_table.select()).fetchall():

            if period.date_from is None:
                period_start = date(today.year, 1, 1)
                self.update_period_record(period, date_from=period_start)

            if period.date_to is None:
                period_end = date(today.year, 12, 31)
                self.update_period_record(period, date_to=period_end)

    def update_period_record(self, period, **kwargs):
        self.execute(
            self.periods_table.update()
            .values(**kwargs)
            .where(self.periods_table.c.id == period.id))

    def make_period_date_columns_non_nullable(self):
        self.op.alter_column('periods', 'date_from',
                             existing_type=Date,
                             nullable=False)
        self.op.alter_column('periods', 'date_to',
                             existing_type=Date,
                             nullable=False)
