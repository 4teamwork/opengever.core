from ftw.upgrade import UpgradeStep


class AddBumblebeeSupportForDocuments(UpgradeStep):
    """Add bumblebee support for documents.
    """

    def __call__(self):
        self.install_upgrade_profile()
