from ftw.upgrade import UpgradeStep


class AddAJavascriptFileForOfficeConnectorURLs(UpgradeStep):
    """Add a javascript file for Office Connector URLs.
    """

    def __call__(self):
        self.install_upgrade_profile()
