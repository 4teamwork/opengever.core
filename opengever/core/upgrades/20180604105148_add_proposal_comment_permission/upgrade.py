from ftw.upgrade import UpgradeStep


class AddProposalCommentPermission(UpgradeStep):
    """Add proposal comment permission.
    """

    # Reindexes the security for all dossiers also for the
    # `20171026172342_add_new_dossier_manager_role` upgradestep.

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_dossier_workflow'],
            reindex_security=False)
