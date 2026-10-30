from ftw.upgrade import UpgradeStep


class AddAlternativeNotificationEmailFlag(UpgradeStep):
    """Register the default-off alternative notification email flag."""

    def __call__(self):
        self.install_upgrade_profile()
