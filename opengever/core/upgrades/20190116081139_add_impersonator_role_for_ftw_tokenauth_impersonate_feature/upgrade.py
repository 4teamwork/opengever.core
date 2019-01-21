from ftw.upgrade import UpgradeStep


class AddImpersonatorRoleForFtwTokenauthImpersonateFeature(UpgradeStep):
    """Add impersonator role for ftw tokenauth impersonate feature.
    """

    def __call__(self):
        self.install_upgrade_profile()
