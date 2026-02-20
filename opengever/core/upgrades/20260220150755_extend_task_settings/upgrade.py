from ftw.upgrade import UpgradeStep


class ExtendTaskSettings(UpgradeStep):
    """Extend task settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
