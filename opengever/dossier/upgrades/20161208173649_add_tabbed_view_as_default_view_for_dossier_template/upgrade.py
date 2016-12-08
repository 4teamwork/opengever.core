from ftw.upgrade import UpgradeStep


class AddTabbedViewAsDefaultViewForDossierTemplate(UpgradeStep):
    """Add tabbed view as default view for dossier template.
    """

    def __call__(self):
        self.install_upgrade_profile()
