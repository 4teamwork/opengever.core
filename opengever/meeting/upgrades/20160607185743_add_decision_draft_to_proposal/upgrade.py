from opengever.base.types import UnicodeCoercingText
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column


class AddDecisionDraftToProposal(SchemaMigration):
    """Add decision draft to proposal.
    """

    def migrate(self):
        self.add_decision_draft_column_on_proposal()

    def add_decision_draft_column_on_proposal(self):
        self.op.add_column(
            'proposals',
            Column('decision_draft', UnicodeCoercingText, nullable=True))
