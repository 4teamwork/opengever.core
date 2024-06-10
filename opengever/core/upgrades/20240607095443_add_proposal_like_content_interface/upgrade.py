from ftw.upgrade import UpgradeStep
from opengever.meeting.proposal import IProposal
from opengever.ris.proposal import IProposal as IRisProposal


class AddProposalLikeContentInterface(UpgradeStep):
    """Add proposal like content interface.
    """

    def __call__(self):
        query = {'object_provides': [
            IRisProposal.__identifier__,
            IProposal.__identifier__,
        ]}

        for obj in self.objects(
                query,
                'Index object_provides to add IPRoposalLikeContent interface in Solr'):
            obj.reindexObject(idxs=['object_provides'])
