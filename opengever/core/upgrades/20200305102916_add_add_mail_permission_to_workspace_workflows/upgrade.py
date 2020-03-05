from ftw.upgrade import UpgradeStep


class AddAddMailPermissionToWorkspaceWorkflows(UpgradeStep):
    """Add the Add Mail permission to workspace workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_folder',
             'opengever_workspace'],
            reindex_security=False)
