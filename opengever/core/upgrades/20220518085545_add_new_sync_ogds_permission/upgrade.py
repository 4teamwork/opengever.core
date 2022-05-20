from ftw.upgrade import UpgradeStep


class AddNewSyncOGDSPermission(UpgradeStep):
    """Add new sync OGDS permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
