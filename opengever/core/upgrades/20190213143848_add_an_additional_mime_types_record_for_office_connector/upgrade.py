from ftw.upgrade import UpgradeStep


class AddAnAdditionalMIMETypesRecordForOfficeConnector(UpgradeStep):
    """Add an additional MIME types record for Office Connector.
    """

    def __call__(self):
        self.install_upgrade_profile()
