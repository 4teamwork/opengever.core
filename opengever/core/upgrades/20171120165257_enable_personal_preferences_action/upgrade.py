from ftw.upgrade import UpgradeStep


class EnablePersonalPreferencesAction(UpgradeStep):
    """Enable personal-preferences action.
    """

    def __call__(self):
        self.install_upgrade_profile()
