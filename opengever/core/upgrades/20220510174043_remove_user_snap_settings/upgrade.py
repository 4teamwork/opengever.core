from ftw.upgrade import UpgradeStep


class RemoveUserSnapSettings(UpgradeStep):
    """Remove user snap settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
