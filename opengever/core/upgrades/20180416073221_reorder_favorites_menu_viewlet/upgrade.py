from ftw.upgrade import UpgradeStep


class ReorderFavoritesMenuViewlet(UpgradeStep):
    """Reorder favorites-menu viewlet.
    """

    def __call__(self):
        self.install_upgrade_profile()
