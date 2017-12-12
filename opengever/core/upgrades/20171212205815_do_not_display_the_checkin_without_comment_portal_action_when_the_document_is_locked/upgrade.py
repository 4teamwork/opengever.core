from ftw.upgrade import UpgradeStep


class DoNotDisplayTheCheckinWithoutCommentPortalActionWhenTheDocumentIsLocked(UpgradeStep):
    """Do not display the checkin-without-comment portal action when the document is locked.
    """

    def __call__(self):
        self.install_upgrade_profile()
