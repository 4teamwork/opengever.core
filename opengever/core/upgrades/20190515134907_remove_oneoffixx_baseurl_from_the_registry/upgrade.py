from ftw.upgrade import UpgradeStep


class RemoveOneoffixxBaseurlFromTheRegistry(UpgradeStep):
    """Remove Oneoffixx baseurl from the registry."""

    def __call__(self):
        self.install_upgrade_profile()
