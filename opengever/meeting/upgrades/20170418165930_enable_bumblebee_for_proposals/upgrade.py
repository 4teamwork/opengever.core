from ftw.upgrade import UpgradeStep
from opengever.meeting.proposal import IProposal


class EnableBumblebeeForProposals(UpgradeStep):
    """Enable bumblebee for proposals.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for obj in self.objects(
                {'object_provides': IProposal.__identifier__},
                'Enable bumblebee on proposals and submitted proposals'):
            obj.reindexObject(idxs=['object_provides'])
            # XXX SHOULD WE STORE IN BUMBLEBEE???
