from ftw.upgrade import UpgradeStep


class AddSourceFileErasmentFlag(UpgradeStep):
    """Add source file erasment flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
