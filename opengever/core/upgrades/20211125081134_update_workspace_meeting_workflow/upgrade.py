from ftw.upgrade import UpgradeStep


class UpdateWorkspaceMeetingWorkflow(UpgradeStep):
    """Update workspace meeting workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace_meeting'], reindex_security=False)
