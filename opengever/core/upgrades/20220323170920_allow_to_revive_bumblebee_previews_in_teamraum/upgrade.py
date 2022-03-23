from ftw.upgrade import UpgradeStep


class AllowToReviveBumblebeePreviewsInTeamraum(UpgradeStep):
    """Allow to revive bumblebee previews in teamraum.
    """

    def __call__(self):
        self.install_upgrade_profile()
