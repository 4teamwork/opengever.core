from ftw.upgrade import UpgradeStep


class AddEditDateOfCassationPermission(UpgradeStep):
    """Add EditDateOfCassation permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
