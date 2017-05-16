from ftw.upgrade import UpgradeStep


class UpdateTaskTemplateFolderWorkflow(UpgradeStep):
    """Update task template folder workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_tasktemplatefolder_workflow'],
            reindex_security=False)
