from ftw.upgrade import UpgradeStep


class UpdateWorkflows(UpgradeStep):
    """Update workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace',
             'opengever_committeecontainer_workflow',
             'opengever_workspace_root',
             'opengever_workspace_folder',
             'opengever_committee_workflow'],
            reindex_security=False)
