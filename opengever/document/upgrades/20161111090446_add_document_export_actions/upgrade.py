from ftw.upgrade import UpgradeStep


class AddDocumentExportActions(UpgradeStep):
    """Add document export actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
