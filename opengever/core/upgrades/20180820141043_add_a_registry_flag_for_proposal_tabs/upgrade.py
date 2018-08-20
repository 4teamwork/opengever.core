from ftw.upgrade import UpgradeStep


class AddARegistryFlagForProposalTabs(UpgradeStep):
    """Add a registry flag for proposal tabs.
    """

    def __call__(self):
        self.install_upgrade_profile()
