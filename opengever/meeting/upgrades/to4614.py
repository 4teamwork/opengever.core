from opengever.core.upgrade import SchemaMigration
from sqlalchemy import DateTime


class AlterProposalHistoryCreatedColumn(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4614

    def migrate(self):
        self.alter_proposalhistory_column()

    def alter_proposalhistory_column(self):
        self.op.alter_column(
            table_name='proposalhistory',
            column_name='created',
            existing_nullable=False,
            type_=DateTime(timezone=True),
        )
