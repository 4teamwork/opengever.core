from ftw.upgrade import UpgradeStep


class AddLinkedWorkspacesBehavior(UpgradeStep):
    """Add linked workspaces behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
