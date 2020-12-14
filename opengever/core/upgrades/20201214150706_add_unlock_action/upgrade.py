from ftw.upgrade import UpgradeStep


class AddUnlockAction(UpgradeStep):
    """Add unlock action.
    """

    def __call__(self):
        self.install_upgrade_profile()
