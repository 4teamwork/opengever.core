from ftw.upgrade import UpgradeStep


class ReindexSearchableTextForDossierTemplates(UpgradeStep):
    """Reindex SearchableText for dossier templates.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_reindex_objects(
            {'portal_type': 'opengever.dossier.dossiertemplate'},
            idxs=['SearchableText'])
