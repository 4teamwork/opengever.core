from ftw.upgrade import UpgradeStep


class RemoveWorkflowForDossierTemplates(UpgradeStep):
    """Remove workflow for dossier templates.
    """

    def __call__(self):
        self.install_upgrade_profile()

        for obj in self.objects(
                {'portal_type': 'opengever.dossier.dossiertemplate'},
                "Reindex object security for dossiertemplates"):
            self.update_security(obj, reindex_security=True)
