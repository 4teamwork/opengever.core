from ftw.upgrade import UpgradeStep


class OrderFavoriteActionViewlet(UpgradeStep):
    """Order favorite action viewlet.
    """

    def __call__(self):
        self.install_upgrade_profile()
