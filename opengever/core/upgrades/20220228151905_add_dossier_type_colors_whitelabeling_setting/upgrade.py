from ftw.upgrade import UpgradeStep


class AddDossierTypeColorsWhitelabelingSetting(UpgradeStep):
    """Add dossier_type_colors whitelabeling setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
