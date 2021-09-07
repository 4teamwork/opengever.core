from ftw.upgrade import UpgradeStep


class FixRepositoryFolderWorkflow(UpgradeStep):
    """Fix repository folder workflow.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_repository_workflow'],
            reindex_security=False)
