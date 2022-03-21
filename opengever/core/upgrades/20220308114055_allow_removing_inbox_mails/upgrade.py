from ftw.upgrade import UpgradeStep


class AllowRemovingInboxMails(UpgradeStep):
    """Allow removing inbox mails.
    """

    def __call__(self):
        self.install_upgrade_profile()
