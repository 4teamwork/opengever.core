from ftw.upgrade import UpgradeStep


class AddARecordOfBlacklistedMIMETypesForOfficeConnector(UpgradeStep):
    """Add a record of blacklisted MIME types for Office Connector.
    """

    def __call__(self):
        self.install_upgrade_profile()
