from ftw.upgrade import UpgradeStep


class PortRepositoryFolderTabsToCode(UpgradeStep):
    """Port repository folder tabs to code.
    """

    def __call__(self):
        self.install_upgrade_profile()
