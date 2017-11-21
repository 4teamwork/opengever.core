from ftw.upgrade import UpgradeStep


class SetTaskCommentPermission(UpgradeStep):
    """Set task comment permission.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Merge update security from
        # - 20161125103319@opengever.dossier:default
        # - 20170301235934@opengever.dossier:default

        # Also reindex security since, 20161125103319@opengever.dossier:default
        # probably indexed the security

        self.update_workflow_security(
            ['opengever_dossier_workflow'], reindex_security=True)
