from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddProposalColumns(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4601

    def migrate(self):
        self.add_additional_poposal_columns()

    def add_additional_poposal_columns(self):
        self.op.add_column('proposals', Column('publish_in', Text))
        self.op.add_column('proposals', Column('disclose_to', Text))
        self.op.add_column('proposals', Column('copy_for_attention', Text))
