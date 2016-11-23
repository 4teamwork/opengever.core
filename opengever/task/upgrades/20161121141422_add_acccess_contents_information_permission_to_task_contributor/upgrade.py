from ftw.upgrade import UpgradeStep


class AddAcccessContentsInformationPermissionToTaskContributor(UpgradeStep):
    """Add acccess contents information permission to task contributor.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # reindex_security is not necessary - View permissions didn't change
        self.update_workflow_security(['opengever_task_workflow'],
                                      reindex_security=False)
