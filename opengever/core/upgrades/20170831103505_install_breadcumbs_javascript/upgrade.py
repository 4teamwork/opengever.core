from ftw.upgrade import UpgradeStep


class InstallBreadcumbsJavascript(UpgradeStep):
    """Install breadcumbs javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
