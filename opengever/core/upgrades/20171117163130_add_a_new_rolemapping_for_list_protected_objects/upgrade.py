from ftw.upgrade import UpgradeStep


class AddANewRolemappingForListProtectedObjects(UpgradeStep):
    """Add a new rolemapping for List Protected Objects.
    """

    def __call__(self):
        self.install_upgrade_profile()
