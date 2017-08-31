from ftw.upgrade import UpgradeStep


class AddDeletePermissionForTemplateFolderWorkflow(UpgradeStep):
    """Add delete permission for template folder workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_templatefolder_workflow'], reindex_security=False)
