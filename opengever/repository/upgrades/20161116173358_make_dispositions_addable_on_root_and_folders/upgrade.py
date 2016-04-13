from ftw.upgrade import UpgradeStep


class MakeDispositionsAddableOnRootAndFolders(UpgradeStep):
    """Make dispositions addable on root and folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
