from ftw.upgrade import UpgradeStep


class AllowAdministratorsToDeactivateDossiers(UpgradeStep):
    """Allow administrators to deactivate dossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()
