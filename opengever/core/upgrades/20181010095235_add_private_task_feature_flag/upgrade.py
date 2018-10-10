from ftw.upgrade import UpgradeStep


class AddPrivateTaskFeatureFlag(UpgradeStep):
    """Add private task feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
