from ftw.upgrade import UpgradeStep


class UpdateCreateProposalAction(UpgradeStep):
    """Update create_proposal action.
    """

    def __call__(self):
        self.install_upgrade_profile()
