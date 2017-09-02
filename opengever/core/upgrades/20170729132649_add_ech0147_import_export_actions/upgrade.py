from ftw.upgrade import UpgradeStep


class AddECH0147ImportExportActions(UpgradeStep):
    """Add ech0147 import export actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
