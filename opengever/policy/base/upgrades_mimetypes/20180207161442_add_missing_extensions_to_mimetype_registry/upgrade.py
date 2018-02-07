from ftw.upgrade import UpgradeStep


class AddMissingExtensionsToMimetypeRegistry(UpgradeStep):
    """Add missing extensions to mimetype registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
