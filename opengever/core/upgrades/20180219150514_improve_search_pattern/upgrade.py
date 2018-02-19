from ftw.upgrade import UpgradeStep


class ImproveSearchPattern(UpgradeStep):
    """Improve search pattern.
    """

    def __call__(self):
        self.install_upgrade_profile()
