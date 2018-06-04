from ftw.upgrade import UpgradeStep


class AddExcelExportActionToRepositoryRootsForAdministrators(UpgradeStep):
    """Add excel export action to repository roots for administrators."""

    def __call__(self):
        self.install_upgrade_profile()
