from ftw.upgrade import UpgradeStep


class AddUserVisibleErrorLogsFeatureFlag(UpgradeStep):
    """Add user visible error logs feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
