from ftw.upgrade import UpgradeStep


class AddIRecentlyTouchedSettingsRegistryRecord(UpgradeStep):
    """Add IRecentlyTouchedSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
