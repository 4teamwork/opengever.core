from ftw.upgrade import UpgradeStep


class AddDeleteWorkspaceFoldersPermission(UpgradeStep):
    """Add delete workspace folders permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace'], reindex_security=False)
