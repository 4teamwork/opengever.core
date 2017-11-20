from ftw.upgrade import UpgradeStep


class PortRepositoryRootTabsToCode(UpgradeStep):
    """Port repository root tabs to code.
    """

    def __call__(self):
        self.install_upgrade_profile()
