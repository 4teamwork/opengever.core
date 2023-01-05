from ftw.upgrade import UpgradeStep


class UpdateWorkflows(UpgradeStep):
    """Update workflows after removing SQL contacts permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_todolist',
             'opengever_committeecontainer_workflow',
             'opengever_committee_workflow',
             'opengever_workspace_folder',
             'opengever_workspace',
             'opengever_workspace_document',
             'opengever_workspace_root',
             'opengever_workspace_todo',
             'opengever_period_workflow'],
            reindex_security=False)
