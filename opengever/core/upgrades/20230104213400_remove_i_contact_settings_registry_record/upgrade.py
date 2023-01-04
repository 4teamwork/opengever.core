from ftw.upgrade import UpgradeStep


class RemoveIContactSettingsRegistryRecord(UpgradeStep):
    """Remove IContactSettings registry record.
    """

    def __call__(self):
        self.install_upgrade_profile()
