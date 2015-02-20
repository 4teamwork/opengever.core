from ftw.upgrade import UpgradeStep


class AlsoManageAddPermissionsForMails(UpgradeStep):
    """Task workflow: Make workflow also manage add permissions for mails,
    the same way it does for documents.

    In particular, this avoids mails being addable in tasks in state
    'tested-and-closed'.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.task.upgrades:4200')

        # reindex_security is not necessary - View permissions didn't change
        self.update_workflow_security(['opengever_task_workflow'],
                                      reindex_security=False)
