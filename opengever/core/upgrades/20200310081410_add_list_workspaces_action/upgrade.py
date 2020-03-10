from ftw.upgrade import UpgradeStep


class AddListWorkspacesAction(UpgradeStep):
    """Add list workspaces action.
    """

    def __call__(self):
        self.install_upgrade_profile()
