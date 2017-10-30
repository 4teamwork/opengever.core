from ftw.upgrade import UpgradeStep


class AddNewDossierManagerRole(UpgradeStep):
    """Add new dossier manager role.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            [
                'opengever_dossier_workflow',
                'opengever_repository_workflow',
            ],
            reindex_security=False)
