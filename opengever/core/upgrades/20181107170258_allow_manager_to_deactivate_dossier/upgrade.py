from ftw.upgrade import UpgradeStep


class AllowManagerToDeactivateDossier(UpgradeStep):
    """Allow manager to deactivate dossier.
    """

    def __call__(self):
        self.install_upgrade_profile()
