from ftw.upgrade import UpgradeStep


class AddGroupWatchersFeatureFlag(UpgradeStep):
    """Add group watchers feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
