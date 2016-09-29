from ftw.upgrade import UpgradeStep


class FixJavascriptDependencies(UpgradeStep):
    """Fix javascript dependencies.
    """

    def __call__(self):
        self.install_upgrade_profile()
