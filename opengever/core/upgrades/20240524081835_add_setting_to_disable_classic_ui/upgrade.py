from ftw.upgrade import UpgradeStep


class AddSettingToDisableClassicUI(UpgradeStep):
    """Add setting to disable classic ui.
    """

    def __call__(self):
        self.install_upgrade_profile()
