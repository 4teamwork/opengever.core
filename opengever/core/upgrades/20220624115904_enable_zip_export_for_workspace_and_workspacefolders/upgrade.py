from ftw.upgrade import UpgradeStep


class EnableZipExportForWorkspaceAndWorkspacefolders(UpgradeStep):
    """Enable Zip export for workspace and workspacefolders.
    """

    def __call__(self):
        self.install_upgrade_profile()
