from ftw.upgrade import UpgradeStep


class AddTitleENToCatalogMetadata(UpgradeStep):
    """Add title en to catalog metadata.
    """

    def __call__(self):
        self.install_upgrade_profile()
