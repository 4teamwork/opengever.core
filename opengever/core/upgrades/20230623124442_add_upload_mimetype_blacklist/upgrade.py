from ftw.upgrade import UpgradeStep


class AddUploadMimetypeBlacklist(UpgradeStep):
    """Add upload mimetype blacklist.
    """

    def __call__(self):
        self.install_upgrade_profile()
