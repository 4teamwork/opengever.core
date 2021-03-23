from ftw.upgrade import UpgradeStep


class AddDossierTypesConfigurationSetting(UpgradeStep):
    """Add dossier_types configuration setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
