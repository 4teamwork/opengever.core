from ftw.upgrade import UpgradeStep


class AddAdditionalTaskStatePlanned(UpgradeStep):
    """Add additional task state planned.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_task_workflow'], reindex_security=False)
