from ftw.upgrade import UpgradeStep


class AddFolderFactoriesToPortalActions(UpgradeStep):
    """Add folder_factories to portal_actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
