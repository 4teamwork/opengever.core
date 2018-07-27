from ftw.upgrade import UpgradeStep


class AddSharingJS(UpgradeStep):
    """Add sharing JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
