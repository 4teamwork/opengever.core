from ftw.upgrade import UpgradeStep


class AddWorkspaceCreationAndLinkingFlags(UpgradeStep):
    """Add workspace creation and linking flags.
    """

    def __call__(self):
        self.install_upgrade_profile()
