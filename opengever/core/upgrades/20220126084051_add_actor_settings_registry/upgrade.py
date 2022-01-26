from ftw.upgrade import UpgradeStep


class AddActorSettingsRegistry(UpgradeStep):
    """Add actor settings registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
