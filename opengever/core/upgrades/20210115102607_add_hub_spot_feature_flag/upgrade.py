from ftw.upgrade import UpgradeStep


class AddHubSpotFeatureFlag(UpgradeStep):
    """Add HubSpot feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
