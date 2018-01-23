from ftw.upgrade import UpgradeStep


class ChangeDefaultViewOfWorkspaceFolder(UpgradeStep):
    """Change default view of WorkspaceFolder.
    """

    def __call__(self):
        self.install_upgrade_profile()
