from ftw.upgrade import UpgradeStep


class DropINameFromTitleFromRepoRoots(UpgradeStep):
    """Drop INameFromTitle from repo roots.
    """

    def __call__(self):
        self.install_upgrade_profile()
