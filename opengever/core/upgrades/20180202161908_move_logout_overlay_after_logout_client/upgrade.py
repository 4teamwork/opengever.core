from ftw.upgrade import UpgradeStep


class MoveLogoutOverlayAfterLogoutClient(UpgradeStep):
    """Move logout overlay after logout client.
    """

    def __call__(self):
        self.install_upgrade_profile()
