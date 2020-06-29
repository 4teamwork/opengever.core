from ftw.upgrade import UpgradeStep


class PointLogoutActionToNewLogoutBrowserView(UpgradeStep):
    """Point logout action to new logout browser view.
    """

    def __call__(self):
        self.install_upgrade_profile()
