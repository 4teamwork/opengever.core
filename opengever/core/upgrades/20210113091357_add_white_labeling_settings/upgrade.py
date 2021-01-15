from ftw.upgrade import UpgradeStep


class AddWhiteLabelingSettings(UpgradeStep):
    """Add white labeling settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
