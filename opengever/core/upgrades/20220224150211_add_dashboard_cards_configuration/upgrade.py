from ftw.upgrade import UpgradeStep


class AddDashboardCardsConfiguration(UpgradeStep):
    """Add dashboard cards configuration.
    """

    def __call__(self):
        self.install_upgrade_profile()
