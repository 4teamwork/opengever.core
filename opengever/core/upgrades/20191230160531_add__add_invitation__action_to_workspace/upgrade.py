from ftw.upgrade import UpgradeStep


class Add_addInvitation_actionToWorkspace(UpgradeStep):
    """Add 'add invitation' action to workspace.
    """

    def __call__(self):
        self.install_upgrade_profile()
