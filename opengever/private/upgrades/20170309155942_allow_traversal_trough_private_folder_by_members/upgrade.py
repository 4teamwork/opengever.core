from ftw.upgrade import UpgradeStep


class AllowTraversalTroughPrivateFolderByMembers(UpgradeStep):
    """Allow traversal trough private folder by members.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_private_root_workflow'],
            reindex_security=False)
