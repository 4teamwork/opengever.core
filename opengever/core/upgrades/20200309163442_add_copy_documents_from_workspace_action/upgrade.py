from ftw.upgrade import UpgradeStep


class AddCopyDocumentsFromWorkspaceAction(UpgradeStep):
    """Add copy documents from workspace action.
    """

    def __call__(self):
        self.install_upgrade_profile()
