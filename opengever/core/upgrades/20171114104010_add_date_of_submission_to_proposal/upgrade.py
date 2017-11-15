from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date


class AddDateOfSubmissionToProposal(SchemaMigration):
    """Add date of submission to proposal.
    """

    def migrate(self):
        self.op.add_column(
            'proposals', Column(
                'date_of_submission', Date(), index=True))
