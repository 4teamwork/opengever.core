from ftw.upgrade import UpgradeStep


class AllowEmailsInWorkspaceFolders(UpgradeStep):
    """Allow emails in workspace folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
