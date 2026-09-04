from ftw.upgrade import UpgradeStep


class AddBackgroundTasksControlpanel(UpgradeStep):
    """Add background tasks controlpanel.
    """

    def __call__(self):
        self.install_upgrade_profile()
