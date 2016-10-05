from ftw.upgrade import UpgradeStep


class ExcludePrivateRootFromNavigation(UpgradeStep):
    """Exclude private root from navigation.
    """

    def __call__(self):
        self.install_upgrade_profile()
