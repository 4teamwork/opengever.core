from ftw.upgrade import UpgradeStep


class AllowReaderToReviveBumblebeePreviews(UpgradeStep):
    """Allow Reader to revive bumblebee previews.
    """

    def __call__(self):
        self.install_upgrade_profile()
