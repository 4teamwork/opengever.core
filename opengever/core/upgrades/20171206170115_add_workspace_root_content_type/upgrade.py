from ftw.upgrade import UpgradeStep


class AddWorkspaceRootContentType(UpgradeStep):
    """Add workspace root content type.
    """

    def __call__(self):
        self.install_upgrade_profile()
