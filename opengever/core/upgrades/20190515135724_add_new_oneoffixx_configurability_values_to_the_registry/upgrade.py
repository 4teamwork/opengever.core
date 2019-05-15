from ftw.upgrade import UpgradeStep


class AddNewOneoffixxConfigurabilityValuesToTheRegistry(UpgradeStep):
    """Add new Oneoffixx configurability values to the registry."""

    def __call__(self):
        self.install_upgrade_profile()
