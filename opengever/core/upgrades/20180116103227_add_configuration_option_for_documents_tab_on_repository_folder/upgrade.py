from ftw.upgrade import UpgradeStep


class AddConfigurationOptionForDocumentsTabOnRepositoryFolder(UpgradeStep):
    """Add configuration option for documents tab on repository folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
