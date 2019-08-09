from ftw.upgrade import UpgradeStep


class AddIFilesystemTransportSettingsRegistryRecord(UpgradeStep):
    """Add IFilesystemTransportSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
