from ftw.upgrade import UpgradeStep


class AddOCDisallowedIPRangeSetting(UpgradeStep):
    """Add oc disallowed ip range setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
