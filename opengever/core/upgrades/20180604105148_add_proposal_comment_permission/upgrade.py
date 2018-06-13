from ftw.upgrade import UpgradeStep


class AddProposalCommentPermission(UpgradeStep):
    """Add proposal comment permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_dossier_workflow'],
            reindex_security=False)
