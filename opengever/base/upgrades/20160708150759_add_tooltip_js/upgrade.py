from ftw.upgrade import UpgradeStep


class AddTooltipJS(UpgradeStep):
    """Add tooltip js.
    """

    def __call__(self):
        self.install_upgrade_profile()
