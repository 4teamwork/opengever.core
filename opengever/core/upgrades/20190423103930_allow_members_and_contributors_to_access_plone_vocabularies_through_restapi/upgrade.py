from ftw.upgrade import UpgradeStep


class AllowMembersAndContributorsToAccessPloneVocabulariesThroughRestapi(UpgradeStep):
    """Allow members and contributors to access plone vocabularies through restapi.
    """

    def __call__(self):
        self.install_upgrade_profile()
