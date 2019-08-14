from ftw.upgrade import UpgradeStep


class FixPermissionForExistingWorkspaces(UpgradeStep):
    """Fix permission for existing workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace'], reindex_security=False)
