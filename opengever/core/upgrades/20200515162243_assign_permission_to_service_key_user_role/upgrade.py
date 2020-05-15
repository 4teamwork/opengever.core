from ftw.upgrade import UpgradeStep


class AssignPermissionToServiceKeyUserRole(UpgradeStep):
    """Assign permission to ServiceKeyUser role.
    """

    def __call__(self):
        self.install_upgrade_profile()
