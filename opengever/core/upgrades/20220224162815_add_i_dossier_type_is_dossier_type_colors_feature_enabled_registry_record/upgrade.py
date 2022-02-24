from ftw.upgrade import UpgradeStep


class AddIDossierTypeIsDossierTypeColorsFeatureEnabledRegistryRecord(UpgradeStep):
    """Add IDossierType.is_dossier_type_colors_feature_enabled registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
