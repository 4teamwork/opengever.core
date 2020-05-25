from ftw.upgrade import UpgradeStep


class HandleLargeContenttrees(UpgradeStep):
    """Handle large contenttrees.
    """

    def __call__(self):
        self.install_upgrade_profile()
