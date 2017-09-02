from ftw.upgrade import UpgradeStep


class AddNewCommitteeRoles(UpgradeStep):
    """Add new committee roles.
    """

    def __call__(self):
        self.install_upgrade_profile()
