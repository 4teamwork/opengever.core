from ftw.upgrade import UpgradeStep


class AddWorkspaceClientSettings(UpgradeStep):
    """Add workspace client settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
