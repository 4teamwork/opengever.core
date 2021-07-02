from ftw.upgrade import UpgradeStep


class AddExportProposalsAction(UpgradeStep):
    """Add export proposals action.
    """

    def __call__(self):
        self.install_upgrade_profile()
