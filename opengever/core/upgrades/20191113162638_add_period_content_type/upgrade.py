from ftw.upgrade import UpgradeStep


class AddPeriodContentType(UpgradeStep):
    """Add period content type.
    """

    def __call__(self):
        self.install_upgrade_profile()
