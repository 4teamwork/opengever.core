from ftw.upgrade import UpgradeStep


class AddDocumentFromOfficeatworkAction(UpgradeStep):
    """Add document from officeatwork action.
    """

    def __call__(self):
        self.install_upgrade_profile()
