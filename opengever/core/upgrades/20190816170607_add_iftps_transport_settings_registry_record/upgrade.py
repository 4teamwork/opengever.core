from ftw.upgrade import UpgradeStep


class AddIFTPSTransportSettingsRegistryRecord(UpgradeStep):
    """Add IFTPSTransportSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
