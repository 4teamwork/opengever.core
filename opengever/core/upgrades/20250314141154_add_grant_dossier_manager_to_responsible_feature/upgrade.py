from ftw.upgrade import UpgradeStep


class AddGrantDossierManagerToResponsibleFeature(UpgradeStep):
    """Add grant dossier manager to responsible feature.
    """

    def __call__(self):
        self.install_upgrade_profile()
