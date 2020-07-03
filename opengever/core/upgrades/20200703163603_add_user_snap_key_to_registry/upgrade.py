from ftw.upgrade import UpgradeStep


class AddUserSnapKeyToRegistry(UpgradeStep):
    """Add user snap key to registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
