from ftw.upgrade import UpgradeStep


class AddRemoveAnyWatcherPermission(UpgradeStep):
    """Add remove any watcher permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
