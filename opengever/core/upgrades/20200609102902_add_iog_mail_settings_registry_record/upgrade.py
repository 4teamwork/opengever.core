from ftw.upgrade import UpgradeStep


class AddIOGMailSettingsRegistryRecord(UpgradeStep):
    """Add IOGMailSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
