from ftw.upgrade import UpgradeStep


class AddTeaser(UpgradeStep):
    """Add teaser.
    """

    def __call__(self):
        self.install_upgrade_profile()
