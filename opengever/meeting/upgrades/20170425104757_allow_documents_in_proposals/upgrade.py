from ftw.upgrade import UpgradeStep


class AllowDocumentsInProposals(UpgradeStep):
    """Allow documents in proposals.
    """

    def __call__(self):
        self.install_upgrade_profile()
