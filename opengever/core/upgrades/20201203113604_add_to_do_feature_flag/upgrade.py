from ftw.upgrade import UpgradeStep


class AddToDoFeatureFlag(UpgradeStep):
    """Add ToDo feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
