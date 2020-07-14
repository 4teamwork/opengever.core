from ftw.upgrade import UpgradeStep


class AssignRoleAssignmentReportsPermission(UpgradeStep):
    """Assign role assignment reports permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
