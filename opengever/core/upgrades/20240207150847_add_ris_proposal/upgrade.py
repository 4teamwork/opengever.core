from ftw.upgrade import UpgradeStep


class AddRisProposal(UpgradeStep):
    """Add ris proposal.
    """

    def __call__(self):
        self.install_upgrade_profile()
