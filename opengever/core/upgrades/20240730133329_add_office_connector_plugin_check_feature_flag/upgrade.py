from ftw.upgrade import UpgradeStep


class AddOfficeConnectorPluginCheckFeatureFlag(UpgradeStep):
    """Add office connector plugin check feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
