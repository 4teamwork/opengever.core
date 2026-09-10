from ftw.upgrade import UpgradeStep


class ImproveTransitionGuardsForTrashedDocuments(UpgradeStep):
    """Improve transition guards for trashed documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
