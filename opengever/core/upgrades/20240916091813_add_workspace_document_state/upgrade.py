from ftw.upgrade import UpgradeStep


class AddWorkspaceDocumentState(UpgradeStep):
    """Add new Workspace Document Final State.
    """

    def __call__(self):
        self.install_upgrade_profile()
