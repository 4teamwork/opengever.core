from ftw.upgrade import UpgradeStep


class AddRemovedState(UpgradeStep):
    """Add mail-state-removed to the mail workflow and updates
    workflow security.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.mail.upgrades:4100')

        self.update_workflow_security(['opengever_mail_workflow'],
                                      reindex_security=False)
