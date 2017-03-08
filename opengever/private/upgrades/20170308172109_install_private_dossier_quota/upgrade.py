from ftw.upgrade import UpgradeStep


class InstallPrivateDossierQuota(UpgradeStep):
    """Install private dossier quota.
    """

    def __call__(self):
        self.install_upgrade_profile()
