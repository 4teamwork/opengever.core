from ftw.upgrade import UpgradeStep


class ReaderGetsViewOnAllTaskStates(UpgradeStep):
    """Reader gets View on all task states.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_task_workflow'], reindex_security=True)
