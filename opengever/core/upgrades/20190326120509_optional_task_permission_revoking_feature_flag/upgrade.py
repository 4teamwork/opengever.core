from ftw.upgrade import UpgradeStep


class OptionalTaskPermissionRevokingFeatureFlag(UpgradeStep):
    """Optional task permission revoking feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
