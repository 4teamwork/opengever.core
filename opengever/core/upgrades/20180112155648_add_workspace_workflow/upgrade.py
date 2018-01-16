from ftw.upgrade import UpgradeStep


class AddWorkspaceWorkflow(UpgradeStep):
    """Add workspace workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace'], reindex_security=False)
