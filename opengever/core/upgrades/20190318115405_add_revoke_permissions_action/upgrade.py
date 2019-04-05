from ftw.upgrade import UpgradeStep


class AddRevokePermissionsAction(UpgradeStep):
    """Add revoke permissions action.
    """

    def __call__(self):
        self.install_upgrade_profile()
