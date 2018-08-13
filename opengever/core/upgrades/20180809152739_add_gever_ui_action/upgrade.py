from ftw.upgrade import UpgradeStep


class AddGeverUIAction(UpgradeStep):
    """Add gever ui action.
    """

    def __call__(self):
        self.install_upgrade_profile()
