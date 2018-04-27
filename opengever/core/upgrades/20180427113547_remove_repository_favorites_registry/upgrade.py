from ftw.upgrade import UpgradeStep


class RemoveRepositoryFavoritesRegistry(UpgradeStep):
    """Remove repository favorites registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
