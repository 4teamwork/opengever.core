from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class ExtendProposalHistory(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4213

    def migrate(self):
        self.extend_proposal_history_table()

    def extend_proposal_history_table(self):
        self.op.add_column(
            'proposalhistory',
            Column('submitted_document_id', Integer,
                   ForeignKey('submitteddocuments.id')))
        self.op.add_column(
            'proposalhistory', Column('submitted_version', Integer))
        self.op.add_column(
            'proposalhistory', Column('document_title', String(256)))
        self.op.add_column(
            'proposalhistory',
            Column('meeting_id', Integer, ForeignKey('meetings.id')))
