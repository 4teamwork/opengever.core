from ftw.upgrade import UpgradeStep


class RemoveNightlyJobsFeatureFlag(UpgradeStep):
    """Remove nightly jobs feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
