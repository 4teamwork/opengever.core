from ftw.upgrade import UpgradeStep


class DonTAcquireViewPermissionOnProposal(UpgradeStep):
    """Don't acquire View permission on proposal.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_proposal_workflow'], reindex_security=True)
