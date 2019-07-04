from ftw.upgrade import UpgradeStep


class AdjustAccessPloneUserInformationPermission(UpgradeStep):
    """Adjust Access Plone user information permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
