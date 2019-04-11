from ftw.upgrade import UpgradeStep


class AllowNonMemberContributorsToUseTheRESTAPI(UpgradeStep):
    """Allow non-member contributors to use the REST API."""

    def __call__(self):
        self.install_upgrade_profile()
