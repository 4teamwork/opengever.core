from ftw.upgrade import UpgradeStep


class AddRefuseTransitionToDispositionWorkflow(UpgradeStep):
    """Add refuse transition to disposition workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=False)
