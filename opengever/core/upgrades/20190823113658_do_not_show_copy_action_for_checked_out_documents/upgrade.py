from ftw.upgrade import UpgradeStep


class DoNotShowCopyActionForCheckedOutDocuments(UpgradeStep):
    """Do not show copy action for checked out documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
