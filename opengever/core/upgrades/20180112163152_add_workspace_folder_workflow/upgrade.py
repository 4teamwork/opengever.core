from ftw.upgrade import UpgradeStep


class AddWorkspaceFolderWorkflow(UpgradeStep):
    """Add workspace folder workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace_folder'], reindex_security=False)
