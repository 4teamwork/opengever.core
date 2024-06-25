from ftw.upgrade import UpgradeStep


class AddErrorLogFeature(UpgradeStep):
    """Add error log feature.
    """

    def __call__(self):
        self.install_upgrade_profile()
