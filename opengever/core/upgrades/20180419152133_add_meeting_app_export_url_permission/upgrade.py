from ftw.upgrade import UpgradeStep


class AddMeetingAppExportURLPermission(UpgradeStep):
    """Add Meeting app export URL permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
