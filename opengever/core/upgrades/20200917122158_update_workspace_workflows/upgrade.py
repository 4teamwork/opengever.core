from ftw.upgrade import UpgradeStep


class UpdateWorkflows(UpgradeStep):
    """Update workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace',
             'opengever_workspace_folder',
             'opengever_workspace_todolist',
             'opengever_workspace_todo',
             'opengever_workspace_document'],
            reindex_security=False)
