from ftw.upgrade import UpgradeStep


class EnableThePloneRestapiGenericsetupProfile(UpgradeStep):
    """Enable the plone.restapi genericsetup profile.
    """

    def __call__(self):
        self.install_upgrade_profile()
