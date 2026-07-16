from ftw.upgrade import UpgradeStep


class AddSIPArchiveDeliveryFeatureFlag(UpgradeStep):
    """Add sip archive delivery feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
