from ftw.upgrade import UpgradeStep


class AddPortalSettingsRegistry(UpgradeStep):
    """Add portal settings registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
