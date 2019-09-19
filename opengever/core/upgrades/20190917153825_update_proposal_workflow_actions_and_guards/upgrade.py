from ftw.upgrade import UpgradeStep


class UpdateProposalWorkflowActionsAndGuards(UpgradeStep):
    """Update proposal workflow actions and guards.
    """

    def __call__(self):
        self.install_upgrade_profile()
