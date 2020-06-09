from ftw.upgrade import UpgradeStep


class AssignTransferPermission(UpgradeStep):
    """Assign transfer permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
