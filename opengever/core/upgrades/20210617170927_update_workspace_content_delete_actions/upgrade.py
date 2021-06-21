from ftw.upgrade import UpgradeStep


class UpdateWorkspaceContentDeleteActions(UpgradeStep):
    """Update workspace content delete actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
