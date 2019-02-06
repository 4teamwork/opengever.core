from ftw.upgrade import UpgradeStep


class MakeTheOneoffixxTimeoutConfigurableViaTheRegistry(UpgradeStep):
    """Make the Oneoffixx timeout configurable via the registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
