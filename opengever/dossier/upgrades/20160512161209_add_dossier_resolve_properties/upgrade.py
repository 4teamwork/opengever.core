from ftw.upgrade import UpgradeStep


class AddDossierResolveProperties(UpgradeStep):
    """Add dossier resolve properties.
    """

    def __call__(self):
        self.install_upgrade_profile()
