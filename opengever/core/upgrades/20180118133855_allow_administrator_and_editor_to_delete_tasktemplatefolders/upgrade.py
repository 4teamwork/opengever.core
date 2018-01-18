from ftw.upgrade import UpgradeStep


class AllowAdministratorAndEditorToDeleteTasktemplatefolders(UpgradeStep):
    """Allow Administrator and Editor to delete tasktemplatefolders.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_tasktemplatefolder_workflow'], reindex_security=False)
