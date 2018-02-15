from ftw.upgrade import UpgradeStep


class EnableMindManagerWithOfficeConnector(UpgradeStep):
    """Enable mind manager with office connector.
    """

    def __call__(self):
        self.install_upgrade_profile()
