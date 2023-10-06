from ftw.upgrade import UpgradeStep


class AddViewDocumentAction(UpgradeStep):
    """Add view document action.
    """

    def __call__(self):
        self.install_upgrade_profile()
