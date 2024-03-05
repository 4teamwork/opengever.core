from ftw.upgrade import UpgradeStep


class AddRisFeatureFlag(UpgradeStep):
    """Add Ris feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
