from ftw.upgrade import UpgradeStep


class AddRoleArchivist(UpgradeStep):
    """Add role archivist.
    """

    def __call__(self):
        self.install_upgrade_profile()
