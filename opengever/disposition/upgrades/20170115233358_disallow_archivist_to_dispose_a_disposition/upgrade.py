from ftw.upgrade import UpgradeStep


class DisallowArchivistToDisposeDispositions(UpgradeStep):
    """Disallow archivist to dispose a disposition.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=False)
