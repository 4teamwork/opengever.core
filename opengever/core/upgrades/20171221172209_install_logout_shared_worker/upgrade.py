from ftw.upgrade import UpgradeStep


class InstallLogoutSharedWorker(UpgradeStep):
    """Install logout shared worker.
    """

    def __call__(self):
        self.install_upgrade_profile()
