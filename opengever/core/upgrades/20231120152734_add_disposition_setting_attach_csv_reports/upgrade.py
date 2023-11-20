from ftw.upgrade import UpgradeStep


class AddDispositionSettingAttachCsvReports(UpgradeStep):
    """Add disposition setting attach_csv_reports.
    """

    def __call__(self):
        self.install_upgrade_profile()
