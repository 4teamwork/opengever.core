from ftw.upgrade import UpgradeStep


class DisableZIPExportOnPloneSite(UpgradeStep):
    """Disable ZIP Export on PloneSite.
    """

    def __call__(self):
        self.install_upgrade_profile()
