from ftw.upgrade import UpgradeStep


class AllowToTrashUntrashAndDeleteDocumentsInWorkspace(UpgradeStep):
    """Allow to trash, untrash and delete documents in workspace.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_workspace_folder',
             'opengever_workspace'],
            reindex_security=False)
