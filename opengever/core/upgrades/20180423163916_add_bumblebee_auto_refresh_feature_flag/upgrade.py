from ftw.upgrade import UpgradeStep


class AddBumblebeeAutoRefreshFeatureFlag(UpgradeStep):
    """Add bumblebee auto refresh feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
