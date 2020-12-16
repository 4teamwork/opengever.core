from ftw.upgrade import UpgradeStep


class AddWorkspaceMeetingFeatureFlag(UpgradeStep):
    """Add workspace meeting feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
