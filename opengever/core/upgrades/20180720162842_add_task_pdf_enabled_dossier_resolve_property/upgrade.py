from ftw.upgrade import UpgradeStep


class AddTaskPdfEnabledDossierResolveProperty(UpgradeStep):
    """Add task pdf enabled dossier resolve property.
    """

    def __call__(self):
        self.install_upgrade_profile()
