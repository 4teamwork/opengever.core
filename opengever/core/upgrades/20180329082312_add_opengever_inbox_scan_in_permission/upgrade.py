from ftw.upgrade import UpgradeStep


class AddOpengeverInboxScanInPermission(UpgradeStep):
    """Add opengever.inbox scan in permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_inbox_workflow'],
                                      reindex_security=False)
