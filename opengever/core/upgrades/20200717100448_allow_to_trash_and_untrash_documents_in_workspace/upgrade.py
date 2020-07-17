from ftw.upgrade import UpgradeStep


class AllowToTrashAndUntrashDocumentsInWorkspace(UpgradeStep):
    """Allow to trash and untrash documents in workspace
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_folder',
             'opengever_workspace'],
            reindex_security=False)
