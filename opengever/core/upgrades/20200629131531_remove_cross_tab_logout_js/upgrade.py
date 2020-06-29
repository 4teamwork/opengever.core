from ftw.upgrade import UpgradeStep


class RemoveCrossTabLogoutJS(UpgradeStep):
    """Remove Cross-Tab-Logout JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
