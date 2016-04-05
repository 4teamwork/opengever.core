from ftw.upgrade import UpgradeStep


class InstallFtwBumblebee(UpgradeStep):
    """Install ftw bumblebee.
    """

    def __call__(self):
        self.install_upgrade_profile()
