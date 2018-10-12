from ftw.upgrade import UpgradeStep


class AddARegistryConfigForTestingOneoffixxWithPresharedSIDs(UpgradeStep):
    """Add a registry config for testing Oneoffixx with preshared SIDs.
    """

    def __call__(self):
        self.install_upgrade_profile()
