from ftw.upgrade import UpgradeStep


class AddWordImplementationFeatureFlag(UpgradeStep):
    """Add word implementation feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
