from ftw.upgrade import UpgradeStep


class InstallPromisePolyfillInJavasriptRegistry(UpgradeStep):
    """Install Promise polyfill in javasript registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
