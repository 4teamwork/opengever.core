from ftw.upgrade import UpgradeStep


class AddBackgroundTasksRegistrySetting(UpgradeStep):
    """Add background tasks registry setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
