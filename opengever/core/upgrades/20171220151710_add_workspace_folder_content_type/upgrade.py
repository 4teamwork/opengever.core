from ftw.upgrade import UpgradeStep


class AddWorkspaceFolderContentType(UpgradeStep):
    """Add workspace folder content type.
    """

    def __call__(self):
        self.install_upgrade_profile()
