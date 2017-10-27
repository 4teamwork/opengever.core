from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


MAX_TITLE_LENGTH = 256


class AddTitleColumnsToProposalSqlModel(SchemaMigration):
    """Add title columns to proposal sql model.
    """

    def migrate(self):
        self.op.add_column(
            'proposals', Column(
                'title', String(MAX_TITLE_LENGTH), index=True))
        self.op.add_column(
            'proposals', Column(
                'submitted_title', String(MAX_TITLE_LENGTH), index=True))
