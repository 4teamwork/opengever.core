from ftw.upgrade import UpgradeStep


class AddFinalStateToDocuments(UpgradeStep):
    """Add final state to documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
