from ftw.upgrade import UpgradeStep


class RemoveCreatorFromRepositoryFolders(UpgradeStep):
    """Remove creator from repository folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
