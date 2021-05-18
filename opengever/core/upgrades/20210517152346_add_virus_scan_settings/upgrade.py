from ftw.upgrade import UpgradeStep


class AddVirusScanSettings(UpgradeStep):
    """Add virus scan settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
