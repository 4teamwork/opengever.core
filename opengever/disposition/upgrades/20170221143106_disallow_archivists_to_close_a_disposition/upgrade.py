from ftw.upgrade import UpgradeStep


class DisallowArchivistsToCloseADisposition(UpgradeStep):
    """Disallow archivists to close a disposition.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=False)
