from ftw.upgrade import UpgradeStep


class RemoveViewAtatPrefixForPersonalPreferencesForNewUICompatibility(UpgradeStep):
    """Remove view atat prefix for personal preferences for new UI compatibility.
    """

    def __call__(self):
        self.install_upgrade_profile()
