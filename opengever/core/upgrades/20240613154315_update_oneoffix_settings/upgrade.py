from ftw.upgrade import UpgradeStep


class UpdateOneoffixSettings(UpgradeStep):
    """Update oneoffix settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
