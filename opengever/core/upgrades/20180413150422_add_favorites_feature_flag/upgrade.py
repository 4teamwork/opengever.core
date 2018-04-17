from ftw.upgrade import UpgradeStep


class AddFavoritesFeatureFlag(UpgradeStep):
    """Add favorites feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
