from ftw.upgrade import UpgradeStep


class AddAdditionalUiAttributesSetting(UpgradeStep):
    """Add additional ui attributes setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
