from ftw.upgrade import UpgradeStep


class EnableFavoriteETag(UpgradeStep):
    """Enable Favorite ETag.
    """

    def __call__(self):
        self.install_upgrade_profile()
