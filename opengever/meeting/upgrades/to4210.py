from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class AddProposalHistory(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4210

    def migrate(self):
        self.add_proposal_history_table()

    def add_proposal_history_table(self):
        self.op.create_table(
            'proposalhistory',
            Column("id", Integer, Sequence("proposal_history_id_seq"),
                   primary_key=True),
            Column("proposal_id", Integer, ForeignKey('proposals.id'),
                   nullable=False),
            Column("created", DateTime, nullable=False),
            Column("userid", String(256), nullable=False),
            Column("proposal_history_type", String(100), nullable=False)
        )
