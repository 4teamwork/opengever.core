from ftw.upgrade import UpgradeStep


class AddModifyArchivalFilePermission(UpgradeStep):
    """Add ModifyArchivalFile permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
