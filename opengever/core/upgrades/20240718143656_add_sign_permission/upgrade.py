from ftw.upgrade import UpgradeStep


class AddSignPermission(UpgradeStep):
    """Add sign permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
