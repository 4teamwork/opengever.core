from ftw.upgrade import UpgradeStep


class AddIDossierBehaviorToDossierTemplate(UpgradeStep):
    """Add IDossier behavior to dossiertemplate.
    """

    def __call__(self):
        self.install_upgrade_profile()
