from ftw.upgrade import UpgradeStep


class AddNewDestroyDossierPermission(UpgradeStep):
    """Add new destroy dossier permission.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Moved to 20170328131435@opengever.dossier:default

        # self.update_workflow_security(
        #     ['opengever_dossier_workflow'], reindex_security=False)
