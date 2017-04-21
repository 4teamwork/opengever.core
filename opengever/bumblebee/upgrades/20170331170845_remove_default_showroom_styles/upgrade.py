from ftw.upgrade import UpgradeStep


class RemoveDefaultShowroomStyles(UpgradeStep):
    """Remove default showroom styles.
    """

    def __call__(self):
        self.install_upgrade_profile()
