from ftw.upgrade import UpgradeStep


class AddFavoriteJS(UpgradeStep):
    """Add Favorite JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
