from ftw.upgrade import UpgradeStep


class DoNotListDossierTemplateInNavigation(UpgradeStep):
    """Do not list dossier template in navigation.
    """

    def __call__(self):
        self.install_upgrade_profile()
