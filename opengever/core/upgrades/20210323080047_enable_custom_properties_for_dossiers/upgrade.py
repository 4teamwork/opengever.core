from ftw.upgrade import UpgradeStep


class EnableCustomPropertiesForDossiers(UpgradeStep):
    """Enable custom properties for dossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()
