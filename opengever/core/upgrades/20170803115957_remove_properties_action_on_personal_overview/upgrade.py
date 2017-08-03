from ftw.upgrade import UpgradeStep


class RemovePropertiesActionOnPersonalOverview(UpgradeStep):
    """Remove properties action on personal overview.
    """

    def __call__(self):
        self.install_upgrade_profile()
