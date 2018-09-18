from ftw.upgrade import UpgradeStep


class RestrictDeleteActionAvailability(UpgradeStep):
    """Restrict delete action availability.
    """

    def __call__(self):
        self.install_upgrade_profile()
