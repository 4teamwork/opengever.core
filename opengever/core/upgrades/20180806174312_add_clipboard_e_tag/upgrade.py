from ftw.upgrade import UpgradeStep


class AddClipboardETag(UpgradeStep):
    """Add clipboard eTag.
    """

    def __call__(self):
        self.install_upgrade_profile()
