from ftw.upgrade import UpgradeStep


class AddSignFeatureFlag(UpgradeStep):
    """Add sign feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
