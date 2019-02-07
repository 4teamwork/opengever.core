from ftw.upgrade import UpgradeStep


class AllowEditorsToViewMails(UpgradeStep):
    """Allow editors to view mails.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_mail_workflow', 'opengever_inbox_mail_workflow'],
            reindex_security=True)
