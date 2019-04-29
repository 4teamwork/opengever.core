from ftw.upgrade import UpgradeStep


class AddNightlyJobsFeatureFlag(UpgradeStep):
    """Add nightly jobs feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
