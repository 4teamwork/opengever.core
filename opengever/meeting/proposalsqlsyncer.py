from opengever.base.model import Session
from opengever.base.oguid import Oguid
from opengever.base.sqlsyncer import SqlSyncer
from opengever.meeting.model.proposal import Proposal


class ProposalSqlSyncer(SqlSyncer):

    def get_proposal(self):
        """Return or create the corresponding proposal model."""

        oguid = Oguid.for_object(self.obj)
        proposal = Proposal.query.get_by_oguid(oguid)
        if proposal is None:
            proposal = Proposal.create_from(self.obj)
            Session.add(proposal)
        return proposal

    def sync_with_sql(self):
        self.get_proposal().sync_with_proposal(self.obj)


class SubmittedProposalSqlSyncer(SqlSyncer):

    def get_proposal(self):
        """Return the corresponding proposal model."""

        oguid = Oguid.for_object(self.obj)
        return Proposal.query.filter_by(submitted_oguid=oguid).one()

    def sync_with_sql(self):
        self.get_proposal().sync_with_submitted_proposal(self.obj)
