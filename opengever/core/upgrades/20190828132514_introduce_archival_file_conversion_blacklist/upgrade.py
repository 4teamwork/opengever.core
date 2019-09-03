from ftw.upgrade import UpgradeStep


class IntroduceArchivalFileConversionBlacklist(UpgradeStep):
    """Introduce archival file conversion blacklist.
    """

    def __call__(self):
        self.install_upgrade_profile()
