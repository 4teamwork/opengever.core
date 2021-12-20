from ftw.upgrade import UpgradeStep


class AddPropertySheetsManagerRole(UpgradeStep):
    """Add PropertySheetsManager role.
    """

    def __call__(self):
        self.install_upgrade_profile()
