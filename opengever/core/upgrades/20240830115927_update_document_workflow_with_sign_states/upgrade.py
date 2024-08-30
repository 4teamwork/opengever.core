from ftw.upgrade import UpgradeStep


class UpdateDocumentWorkflowWithSignStates(UpgradeStep):
    """Update document workflow with sign states.
    """

    def __call__(self):
        self.install_upgrade_profile()
