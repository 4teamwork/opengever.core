from ftw.upgrade import UpgradeStep


class AddFolderButtonDeleteAction(UpgradeStep):
    """Add folder button delete action.
    """

    def __call__(self):
        self.install_upgrade_profile()
