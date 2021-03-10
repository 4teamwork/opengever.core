from ftw.upgrade import UpgradeStep


class AddMailDownloadSettings(UpgradeStep):
    """Add mail download settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
