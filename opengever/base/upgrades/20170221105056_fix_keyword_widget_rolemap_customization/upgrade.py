from ftw.upgrade import UpgradeStep


class FixKeywordWidgetRolemapCustomization(UpgradeStep):
    """Fix keyword widget rolemap customization.
    """

    def __call__(self):
        self.install_upgrade_profile()
