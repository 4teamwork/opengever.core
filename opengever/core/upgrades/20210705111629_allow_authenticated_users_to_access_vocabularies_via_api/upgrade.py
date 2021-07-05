from ftw.upgrade import UpgradeStep


class AllowAuthenticatedUsersToAccessVocabulariesViaAPI(UpgradeStep):
    """Allow Authenticated users to access vocabularies via API.
    """

    def __call__(self):
        self.install_upgrade_profile()
