from ftw.upgrade import UpgradeStep


class AddResponsibleOrgUnitFieldToRepositoryFolders(UpgradeStep):
    """Add responsible org unit field to repository folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
