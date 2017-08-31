from ftw.upgrade import UpgradeStep


class AddMailPreviewTabRegistryFlag(UpgradeStep):
    """Add mail preview tab registry flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
