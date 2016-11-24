from ftw.upgrade import UpgradeStep


class InstallDisposition(UpgradeStep):
    """Install Disposition.
    """

    def __call__(self):
        self.install_upgrade_profile()
