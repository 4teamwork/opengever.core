from ftw.upgrade import UpgradeStep


class UpdateTaskWorkflow(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.task.upgrades:2603')
        self.update_workflow_security(['opengever_task_workflow'],
                                      reindex_security=False)
