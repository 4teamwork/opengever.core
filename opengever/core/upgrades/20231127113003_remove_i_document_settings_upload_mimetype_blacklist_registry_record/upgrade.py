from ftw.upgrade import UpgradeStep


class RemoveIDocumentSettingsUploadMimetypeBlacklistRegistryRecord(UpgradeStep):
    """Remove IDocumentSettings.upload_mimetype_blacklist registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
