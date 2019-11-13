from ftw.upgrade import UpgradeStep


class AddPeriodPermission(UpgradeStep):
    """Add period permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
