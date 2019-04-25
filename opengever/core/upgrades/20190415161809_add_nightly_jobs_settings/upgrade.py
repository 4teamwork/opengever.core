from ftw.upgrade import UpgradeStep


class AddNightlyJobsSettings(UpgradeStep):
    """Add nightly jobs settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
