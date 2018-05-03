from ftw.upgrade import UpgradeStep


class EnableFavoritesFeatureByDefault(UpgradeStep):
    """Enable favorites feature by default.
    """

    def __call__(self):
        self.install_upgrade_profile()
