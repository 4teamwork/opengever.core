from ftw.upgrade import UpgradeStep


class AddViewPermissionForReaderForForwardingWorkflow(UpgradeStep):
    """Add view permission for reader for forwarding workflow"""

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_forwarding_workflow'],
            reindex_security=True
        )
