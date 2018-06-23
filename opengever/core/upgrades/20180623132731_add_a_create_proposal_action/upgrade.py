from ftw.upgrade import UpgradeStep


class AddACreateProposalAction(UpgradeStep):
    """Add a create proposal action.
    """

    def __call__(self):
        self.install_upgrade_profile()
