from ftw.upgrade import UpgradeStep


class RegisterEtagValueForRepositoryFavorites(UpgradeStep):
    """Register etag value for repository favorites.
    """

    def __call__(self):
        self.install_upgrade_profile()
