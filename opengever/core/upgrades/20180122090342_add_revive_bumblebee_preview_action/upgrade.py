from ftw.upgrade import UpgradeStep


class AddReviveBumblebeePreviewAction(UpgradeStep):
    """Add revive bumblebee preview action.
    """

    def __call__(self):
        self.install_upgrade_profile()
