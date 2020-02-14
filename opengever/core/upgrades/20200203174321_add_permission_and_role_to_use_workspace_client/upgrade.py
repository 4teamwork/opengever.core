from ftw.upgrade import UpgradeStep


class AddPermissionAndRoleToUseWorkspaceClient(UpgradeStep):
    """Add permission and role to use workspace client.
    """

    def __call__(self):
        self.install_upgrade_profile()
