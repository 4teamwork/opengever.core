from ftw.upgrade import UpgradeStep


class AddMSPublisherToOCEditables(UpgradeStep):
    """Add MS Publisher to OC editables.
    """

    def __call__(self):
        self.install_upgrade_profile()
