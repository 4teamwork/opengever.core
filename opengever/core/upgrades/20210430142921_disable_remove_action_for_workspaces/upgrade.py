from ftw.upgrade import UpgradeStep


class DisableRemoveActionForWorkspaces(UpgradeStep):
    """Disable remove action for workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
