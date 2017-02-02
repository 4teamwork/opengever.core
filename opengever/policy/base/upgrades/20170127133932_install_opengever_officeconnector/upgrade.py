from ftw.upgrade import UpgradeStep


class InstallOpengeverOfficeConnector(UpgradeStep):
    """Install opengever Office Connector.
    """

    def __call__(self):
        self.install_upgrade_profile()
