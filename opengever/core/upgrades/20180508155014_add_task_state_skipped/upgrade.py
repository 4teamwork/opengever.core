from ftw.upgrade import UpgradeStep


class AddTaskStateSkipped(UpgradeStep):
    """Add task state skipped.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Skip the workflow security updating of all tasks because it's done by
        # the later upgradestep
        # 20181019172817_reader_gets_view_on_all_task_states anyways

        # self.update_workflow_security(
        #     ['opengever_task_workflow'], reindex_security=False)
