from ftw.upgrade import UpgradeStep


class AddOnlyOfficeIntegration(UpgradeStep):
    """Add OnlyOffice integration.
    """

    def __call__(self):
        self.install_upgrade_profile()
