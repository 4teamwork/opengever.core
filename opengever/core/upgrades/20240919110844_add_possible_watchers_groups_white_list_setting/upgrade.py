from ftw.upgrade import UpgradeStep


class AddPossibleWatchersGroupsWhiteListSetting(UpgradeStep):
    """Add possible watchers groups white list setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
