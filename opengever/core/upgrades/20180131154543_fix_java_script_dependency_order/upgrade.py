from ftw.upgrade import UpgradeStep


class FixJavaScriptDependencyOrder(UpgradeStep):
    """Fix java script dependency order.
    """

    def __call__(self):
        self.install_upgrade_profile()
