from ftw.upgrade import UpgradeStep


class AddCopyActionForSingleDocuments(UpgradeStep):
    """Add copy action for single documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
