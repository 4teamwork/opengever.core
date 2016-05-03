from ftw.upgrade import UpgradeStep


class InstallFtwShowroom(UpgradeStep):
    """Install ftw showroom.
    """

    def __call__(self):
        self.install_upgrade_profile()
