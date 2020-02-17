from ftw.upgrade import UpgradeStep


class AllowAdministratorsToAddNewKeywords(UpgradeStep):
    """Allow administrators to add new keywords.
    """

    def __call__(self):
        self.install_upgrade_profile()
