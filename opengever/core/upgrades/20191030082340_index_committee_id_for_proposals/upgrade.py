from ftw.upgrade import UpgradeStep
from opengever.meeting.proposal import IBaseProposal


class IndexCommitteeIdForProposals(UpgradeStep):
    """Index committee id for proposals.
    The committee id is indexed in the responsible index.
    """

    deferrable = True

    def __call__(self):
        for proposal in self.objects(
                {'object_provides': IBaseProposal.__identifier__},
                'Index committee id for all proposal-ish.'):

            proposal.reindexObject(idxs=['responsible'])
