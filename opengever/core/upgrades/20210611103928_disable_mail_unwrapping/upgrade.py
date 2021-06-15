from ftw.upgrade import UpgradeStep


class DisableMailUnwrapping(UpgradeStep):
    """Disable mail unwrapping.
    """

    def __call__(self):
        self.install_upgrade_profile()
