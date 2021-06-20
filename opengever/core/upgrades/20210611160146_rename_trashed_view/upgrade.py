from ftw.upgrade import UpgradeStep


class RenameTrashedView(UpgradeStep):
    """Rename trashed view.
    """

    def __call__(self):
        self.install_upgrade_profile()
