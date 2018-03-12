from ftw.upgrade import UpgradeStep


class AddServiceKeyUserRoleToIntegrateFtwTokenauth(UpgradeStep):
    """Add ServiceKeyUser role to integrate ftw.tokenauth.
    """

    def __call__(self):
        self.install_upgrade_profile()
