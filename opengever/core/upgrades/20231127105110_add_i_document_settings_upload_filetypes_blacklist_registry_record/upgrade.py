from ftw.upgrade import UpgradeStep


class AddIDocumentSettingsUploadFiletypesBlacklistRegistryRecord(UpgradeStep):
    """Add IDocumentSettings.upload_filetypes_blacklist registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
