from ftw.upgrade import UpgradeStep


class AddSaveAsPDFFeatureFlag(UpgradeStep):
    """Add save as pdf feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
