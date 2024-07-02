from ftw.upgrade import UpgradeStep


class AddManageGroupsAsWatchersPermission(UpgradeStep):
    """Add manage groups as watchers permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
