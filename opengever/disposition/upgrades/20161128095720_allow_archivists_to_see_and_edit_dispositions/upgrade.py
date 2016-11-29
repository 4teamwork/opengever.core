from ftw.upgrade import UpgradeStep


class AllowArchivistsToSeeAndEditDispositions(UpgradeStep):
    """Allow archivists to see and edit dispositions.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=True)
