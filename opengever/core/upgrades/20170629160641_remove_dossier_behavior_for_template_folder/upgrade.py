from ftw.upgrade import UpgradeStep


class RemoveDossierBehaviorForTemplateFolder(UpgradeStep):
    """Remove dossier behavior for template folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
