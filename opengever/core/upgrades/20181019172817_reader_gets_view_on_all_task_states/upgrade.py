from ftw.upgrade import UpgradeStep


class ReaderGetsViewOnAllTaskStates(UpgradeStep):
    """Reader gets View on all task states.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Reindex is also done for the earlier upgradesteps
        # - 20180503231632_add_additional_task_state_planed
        # - 20180508155014_add_task_state_skipped
        # - 20180515125607_add_task_transition_in_progress_to_cancelled
        # where we skip the workflow security update to reduce update-time.
        self.update_workflow_security(['opengever_task_workflow'], reindex_security=True)
