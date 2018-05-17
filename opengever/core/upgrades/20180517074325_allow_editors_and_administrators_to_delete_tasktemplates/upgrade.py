from ftw.upgrade import UpgradeStep


class AllowEditorsAndAdministratorsToDeleteTasktemplates(UpgradeStep):
    """Allow editors and administrators to delete tasktemplates.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_tasktemplate_workflow'],
            reindex_security=False)
