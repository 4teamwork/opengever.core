from ftw.upgrade import UpgradeStep


class UpdateFtwMail(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.inbox.upgrades:2603')

        self.update_workflow_security(['opengever_inbox_workflow'],
                                      reindex_security=True)
