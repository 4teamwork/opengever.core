from ftw.upgrade import UpgradeStep


class AddTaskTransitionInProgressToCancelled(UpgradeStep):
    """Add task transition in progress to cancelled.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_task_workflow'], reindex_security=False)
