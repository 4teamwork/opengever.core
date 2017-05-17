from ftw.upgrade import UpgradeStep


class RemoveCreatorFromPrivateFolders(UpgradeStep):
    """Remove creator from private folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
