from ftw.upgrade import UpgradeStep


class AddTaskStateSkipped(UpgradeStep):
    """Add task state skipped.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_task_workflow'], reindex_security=False)
