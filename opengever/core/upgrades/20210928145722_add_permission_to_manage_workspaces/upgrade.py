from ftw.upgrade import UpgradeStep


class AddPermissionToManageWorkspaces(UpgradeStep):
    """Add permission to manage workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
