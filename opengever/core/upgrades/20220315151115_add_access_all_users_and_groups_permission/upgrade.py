from ftw.upgrade import UpgradeStep


class AddAccessAllUsersAndGroupsPermission(UpgradeStep):
    """Add access all users and groups permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
