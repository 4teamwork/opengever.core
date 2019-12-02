from ftw.upgrade import UpgradeStep


class UpdateWorkflows(UpgradeStep):
    """Update workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_folder',
             'opengever_workspace_root',
             'opengever_workspace_todo',
             'opengever_workspace_todolist',
             'opengever_committee_workflow',
             'opengever_period_workflow',
             'opengever_committeecontainer_workflow',
             'opengever_workspace'],
            reindex_security=False)
