from ftw.upgrade import UpgradeStep


class AddFactoryActionToRepositoryFolderToAddDossierFromTemplate(UpgradeStep):
    """Add factory action to repository folder to add dossier from template.
    """

    def __call__(self):
        self.install_upgrade_profile()
