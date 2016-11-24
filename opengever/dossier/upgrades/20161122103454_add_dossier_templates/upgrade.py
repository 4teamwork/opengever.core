from ftw.upgrade import UpgradeStep


class AddDossierTemplates(UpgradeStep):
    """Add dossier templates.
    """

    def __call__(self):
        self.install_upgrade_profile()
