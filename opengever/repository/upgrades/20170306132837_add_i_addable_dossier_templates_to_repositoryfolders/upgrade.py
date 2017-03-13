from ftw.upgrade import UpgradeStep


class AddIRestrictAddableDossierTemplatesToRepositoryfolders(UpgradeStep):
    """Add IRestrictAddableDossierTemplates to repositoryfolders.
    """

    def __call__(self):
        self.install_upgrade_profile()
