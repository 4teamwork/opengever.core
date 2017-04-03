from ftw.upgrade import UpgradeStep


class AddOfficeConnectorMultiAttachActionToDocuments(UpgradeStep):
    """Add office connector multi attach action to documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
