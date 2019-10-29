from ftw.upgrade import UpgradeStep


class AddUISwitcher(UpgradeStep):
    """Add ui switcher.
    """

    def __call__(self):
        self.install_upgrade_profile()
