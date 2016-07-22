from ftw.upgrade import UpgradeStep


class AddFeatureFlag(UpgradeStep):
    """Add feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
