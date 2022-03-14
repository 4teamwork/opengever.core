from ftw.upgrade import UpgradeStep


class AddDossierChecklistFeatureFlag(UpgradeStep):
    """Add dossier_checklist feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
