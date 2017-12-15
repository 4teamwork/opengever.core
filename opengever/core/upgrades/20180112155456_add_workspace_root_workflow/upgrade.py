from ftw.upgrade import UpgradeStep


class AddWorkspaceRootWorkflow(UpgradeStep):
    """Add workspace root workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace_root'], reindex_security=False)
