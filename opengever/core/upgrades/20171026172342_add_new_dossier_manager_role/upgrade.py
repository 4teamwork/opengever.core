from ftw.upgrade import UpgradeStep


class AddNewDossierManagerRole(UpgradeStep):
    """Add new dossier manager role.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Skip security reindexing of dossiers, because it's done by
        # the later upgradestep
        # `20180604105148_add_proposal_comment_permission` anyways.

        # self.update_workflow_security(
        #     [
        #         'opengever_dossier_workflow',
        #         'opengever_repository_workflow',
        #     ],
        #     reindex_security=False)

        self.update_workflow_security(
            [
                'opengever_repository_workflow',
            ],
            reindex_security=False)
