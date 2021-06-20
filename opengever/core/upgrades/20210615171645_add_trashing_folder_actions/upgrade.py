from ftw.upgrade import UpgradeStep


class AddTrashingFolderActions(UpgradeStep):
    """Add trashing folder actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
