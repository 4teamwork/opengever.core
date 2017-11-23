from ftw.upgrade import UpgradeStep


class AddOGDSSyncConfiguration(UpgradeStep):
    """Add OGDS sync configuration.
    """

    def __call__(self):
        self.install_upgrade_profile()
