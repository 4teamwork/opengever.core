from ftw.upgrade import UpgradeStep


class UpdateDispositionWorkflow(UpgradeStep):
    """Update disposition workflow
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=True)
