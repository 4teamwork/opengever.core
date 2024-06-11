from ftw.upgrade import UpgradeStep


class AddWorkspaceExportParticipantsPermission(UpgradeStep):
    """Add workspace export participants permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
