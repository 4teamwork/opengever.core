from ftw.upgrade import UpgradeStep


class AddDocumentActionsForAPI(UpgradeStep):
    """Add document actions for api.
    """

    def __call__(self):
        self.install_upgrade_profile()
