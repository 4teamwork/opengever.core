from ftw.upgrade import UpgradeStep


class HomogenizeECH0147ImportExportActionTitles(UpgradeStep):
    """Homogenize eCH-0147 Import/Export Action titles.
    """

    def __call__(self):
        self.install_upgrade_profile()
