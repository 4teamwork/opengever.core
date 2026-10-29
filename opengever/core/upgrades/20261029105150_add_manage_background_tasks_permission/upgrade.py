from ftw.upgrade import UpgradeStep


class AddManageBackgroundTasksPermission(UpgradeStep):
    """Add manage background tasks permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
