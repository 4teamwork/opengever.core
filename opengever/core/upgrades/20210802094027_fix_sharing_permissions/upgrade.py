from ftw.upgrade import UpgradeStep


class FixSharingPermissions(UpgradeStep):
    """Fix sharing permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_inbox_document_workflow',
             'opengever_private_document_workflow',
             'opengever_tasktemplatefolder_workflow'],
            reindex_security=False)
