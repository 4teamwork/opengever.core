from ftw.upgrade import UpgradeStep


class InstallJqueryMigration(UpgradeStep):
    """Install jquery migration.
    """

    def __call__(self):
        self.install_upgrade_profile()
