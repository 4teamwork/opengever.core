from ftw.upgrade import UpgradeStep


class InstallCustomEventPolyfillInJavasriptRegistry(UpgradeStep):
    """Install CustomEvent polyfill in javasript registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
