from ftw.upgrade import UpgradeStep


class AllowSharingActionOnWorkspaces(UpgradeStep):
    """Allow sharing action on workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
