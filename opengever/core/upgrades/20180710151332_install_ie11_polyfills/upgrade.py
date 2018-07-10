from ftw.upgrade import UpgradeStep


class InstallIE11Polyfills(UpgradeStep):
    """Install ie11 polyfills.
    """

    def __call__(self):
        self.install_upgrade_profile()
