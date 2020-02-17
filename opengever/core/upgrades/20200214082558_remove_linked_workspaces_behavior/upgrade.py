from ftw.upgrade import UpgradeStep


class RemoveLinkedWorkspacesBehavior(UpgradeStep):
    """Remove linked workspaces behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
