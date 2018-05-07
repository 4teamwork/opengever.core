from ftw.upgrade import UpgradeStep


class CreateNewTeamAddAndEditPermissions(UpgradeStep):
    """Create new team add and edit permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
