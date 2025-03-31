from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.meeting.proposal import IProposal
from opengever.ris.proposal import IProposal as IRisProposal


class ReindexCommittee(UpgradeStep):
    """
    Reindex committee
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': [
            IRisProposal.__identifier__,
            IProposal.__identifier__,
        ]}

        with NightlyIndexer(idxs=["committee"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index committee in Solr'):
                indexer.add_by_brain(brain)
