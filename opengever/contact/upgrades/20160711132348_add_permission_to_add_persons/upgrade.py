from ftw.upgrade import UpgradeStep


class AddPermissionToAddPersons(UpgradeStep):
    """Add permission to add persons.
    """

    def __call__(self):
        self.install_upgrade_profile()
