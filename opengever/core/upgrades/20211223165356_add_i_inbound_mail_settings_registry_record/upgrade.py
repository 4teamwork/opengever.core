from ftw.upgrade import UpgradeStep


class AddIInboundMailSettingsRegistryRecord(UpgradeStep):
    """Add IInboundMailSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
