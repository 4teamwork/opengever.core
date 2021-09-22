from ftw.upgrade import UpgradeStep


class AddPermissionToEditClassifiacationAndLifecycleFields(UpgradeStep):
    """Add permission to edit classification and lifecycle fields.
    """

    def __call__(self):
        self.install_upgrade_profile()
