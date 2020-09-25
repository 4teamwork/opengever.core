from ftw.upgrade import UpgradeStep


class AddManageGroupsPermission(UpgradeStep):
    """Add manage groups permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
