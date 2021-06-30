from ftw.upgrade import UpgradeStep


class RemoveDocumentWatcherFeatureFlag(UpgradeStep):
    """Remove document watcher feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
