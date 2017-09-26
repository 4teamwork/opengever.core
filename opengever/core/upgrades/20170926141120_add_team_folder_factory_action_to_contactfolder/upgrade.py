from ftw.upgrade import UpgradeStep


class AddTeamFolderFactoryActionToContactfolder(UpgradeStep):
    """Add team folder factory action to contactfolder.
    """

    def __call__(self):
        self.install_upgrade_profile()
