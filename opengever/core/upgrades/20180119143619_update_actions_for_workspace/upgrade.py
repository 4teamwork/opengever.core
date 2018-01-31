from ftw.upgrade import UpgradeStep


class UpdateActionsForWorkspace(UpgradeStep):
    """Update Actions for Workspace.
    """

    def __call__(self):
        self.install_upgrade_profile()
