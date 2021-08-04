from ftw.upgrade import UpgradeStep


class AddUnlinkWorkspaceAction(UpgradeStep):
    """Add unlink_workspace action.
    """

    def __call__(self):
        self.install_upgrade_profile()
