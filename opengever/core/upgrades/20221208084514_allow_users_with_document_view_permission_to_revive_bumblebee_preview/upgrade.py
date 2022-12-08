from ftw.upgrade import UpgradeStep


class AllowUsersWithDocumentViewPermissionToReviveBumblebeePreview(UpgradeStep):
    """Allow users with document view permission to revive bumblebee preview.
    """

    def __call__(self):
        self.install_upgrade_profile()
