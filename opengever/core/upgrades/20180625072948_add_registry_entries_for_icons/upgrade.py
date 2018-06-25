from ftw.upgrade import UpgradeStep


class AddRegistryEntriesForIcons(UpgradeStep):
    """Add registry entries for icons.
    """

    def __call__(self):
        self.install_upgrade_profile()
