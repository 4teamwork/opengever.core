from ftw.upgrade import UpgradeStep


class AddWOPIIntegration(UpgradeStep):
    """Add WOPI integration.
    """

    def __call__(self):
        self.install_upgrade_profile()
