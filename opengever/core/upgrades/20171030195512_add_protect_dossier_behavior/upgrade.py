from ftw.upgrade import UpgradeStep


class AddProtectDossierBehavior(UpgradeStep):
    """Add protect dossier behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
