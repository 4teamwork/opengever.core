from ftw.upgrade import UpgradeStep


class RemoveCreatorFromDocuments(UpgradeStep):
    """Remove creator from documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
