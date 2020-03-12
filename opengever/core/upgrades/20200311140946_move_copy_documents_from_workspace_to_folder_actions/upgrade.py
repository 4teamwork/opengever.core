from ftw.upgrade import UpgradeStep


class MoveCopyDocumentsFromWorkspaceToFolderActions(UpgradeStep):
    """Move copy documents from workspace to folder actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
