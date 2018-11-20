from ftw.upgrade import UpgradeStep


class AddOfficeConnectorTUSUploadSettings(UpgradeStep):
    """Add Office Connector TUS upload settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
