from ftw.upgrade import UpgradeStep


class FixInboxDocumentWorkflow(UpgradeStep):
    """Fix inbox document workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
