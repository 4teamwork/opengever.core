from ftw.upgrade import UpgradeStep


class AddCopyDocumentsToWorkspaceAction(UpgradeStep):
    """Add copy documents to workspace action.
    """

    def __call__(self):
        self.install_upgrade_profile()
