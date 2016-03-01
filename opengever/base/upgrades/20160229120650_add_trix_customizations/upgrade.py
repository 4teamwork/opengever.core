from ftw.upgrade import UpgradeStep


class AddTrixCustomizations(UpgradeStep):
    """Add trix customizations.
    """

    def __call__(self):
        self.install_upgrade_profile()
