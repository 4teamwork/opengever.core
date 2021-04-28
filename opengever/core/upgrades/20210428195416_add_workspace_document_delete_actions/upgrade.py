from ftw.upgrade import UpgradeStep


class AddWorkspaceDocumentDeleteActions(UpgradeStep):
    """Add workspace document delete actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
