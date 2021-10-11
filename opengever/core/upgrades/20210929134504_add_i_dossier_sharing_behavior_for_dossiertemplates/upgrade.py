from ftw.upgrade import UpgradeStep


class AddIDossierSharingBehaviorForDossiertemplates(UpgradeStep):
    """Add IDossier Sharing behavior for dossiertemplates.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for dossiertemplates in self.objects(
                {'portal_type': 'opengever.dossier.dossiertemplate'},
                'Reindex object_provides for all dossiertemplates.'):

            dossiertemplates.reindexObject(idxs=['object_provides'])
