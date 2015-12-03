from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddCommentColumnToProposalHistory(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4625

    def migrate(self):
        self.add_text_to_history()

    def add_text_to_history(self):
        self.op.add_column(
            'proposalhistory',
            Column('text', Text))
