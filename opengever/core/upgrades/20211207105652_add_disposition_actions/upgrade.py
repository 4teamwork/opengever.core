from ftw.upgrade import UpgradeStep


class AddDispositionActions(UpgradeStep):
    """Add disposition actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
