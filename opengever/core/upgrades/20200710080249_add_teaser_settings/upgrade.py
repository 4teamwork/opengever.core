from ftw.upgrade import UpgradeStep


class AddTeaserSettings(UpgradeStep):
    """Add teaser settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
