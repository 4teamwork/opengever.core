from ftw.upgrade import UpgradeStep


class MakePrivateDossierViewableForAdministrator(UpgradeStep):
    """Make private dossier viewable for Administrator.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_private_dossier_workflow',
             'opengever_private_folder_workflow'],
            reindex_security=True)
