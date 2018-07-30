from ftw.upgrade import UpgradeStep


class RemoveLogoutOverlay(UpgradeStep):
    """Remove logout overlay.
    """

    def __call__(self):
        self.install_upgrade_profile()
