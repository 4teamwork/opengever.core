from ftw.upgrade import UpgradeStep


class AdjustActionPermissionForDossierTemplate(UpgradeStep):
    """Adjust action permission for dossier template.
    """

    def __call__(self):
        self.install_upgrade_profile()
