from ftw.upgrade import UpgradeStep


class AddSaveDocumentAsPdfAction(UpgradeStep):
    """Add save document as pdf action.
    """

    def __call__(self):
        self.install_upgrade_profile()
