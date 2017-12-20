from ftw.upgrade import UpgradeStep


class AddWorkspaceContentType(UpgradeStep):
    """Add workspace content type.
    """

    def __call__(self):
        self.install_upgrade_profile()
