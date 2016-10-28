from ftw.upgrade import UpgradeStep


class UpdateShowroomDependencies(UpgradeStep):
    """Update showroom dependencies.
    """

    def __call__(self):
        self.install_upgrade_profile()
