from ftw.upgrade import UpgradeStep


class ConfigureTabbedviewEtagInCaching(UpgradeStep):
    """Configure tabbedview etag in caching.
    """

    def __call__(self):
        self.install_upgrade_profile()
