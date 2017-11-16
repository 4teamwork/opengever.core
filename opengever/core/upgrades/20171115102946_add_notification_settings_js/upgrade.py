from ftw.upgrade import UpgradeStep


class AddNotificationSettingsJS(UpgradeStep):
    """Add notification settings JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
