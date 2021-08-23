from ftw.upgrade import UpgradeStep


class AddProtectDossierAction(UpgradeStep):
    """Add protect dossier action.
    """

    def __call__(self):
        self.install_upgrade_profile()
