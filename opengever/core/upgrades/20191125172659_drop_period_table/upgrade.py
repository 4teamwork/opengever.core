from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import itertools
import logging


LOG = logging.getLogger('ftw.upgrade')


periods_table = table(
    'periods',
    column('id'),
)


class NonEmptyPeriodsTable(Exception):
    """Raised when migration precondition is violated."""


class DropPeriodTable(SchemaMigration):
    """Drop period table.

    All periods should have been migrated by previous migrations. If not
    upgrades were not executed correctly and we MUST abort to remain in a
    consistent state.
    """

    def migrate(self):
        current_period_ids = self.get_period_ids()
        if current_period_ids:
            raise NonEmptyPeriodsTable(
                "Expected empty period table, found {} peridos with the "
                "following ids: {}".format(
                    len(current_period_ids), repr(current_period_ids)))

        self.op.drop_table('periods')

    def get_period_ids(self):
        statement = select([periods_table.c.id])
        result_rows = list(self.execute(statement).fetchall())

        period_ids = list(itertools.chain(*result_rows))
        return period_ids
