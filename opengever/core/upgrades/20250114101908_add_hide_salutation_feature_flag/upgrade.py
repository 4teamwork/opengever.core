from ftw.upgrade import UpgradeStep


class AddHideSalutationFeatureFlag(UpgradeStep):
    """Add hide salutation feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
