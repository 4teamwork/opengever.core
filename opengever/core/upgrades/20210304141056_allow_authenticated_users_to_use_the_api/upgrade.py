from ftw.upgrade import UpgradeStep


class AllowAuthenticatedUsersToUseTheAPI(UpgradeStep):
    """Allow Authenticated Users to use the API.
    """

    def __call__(self):
        self.install_upgrade_profile()
