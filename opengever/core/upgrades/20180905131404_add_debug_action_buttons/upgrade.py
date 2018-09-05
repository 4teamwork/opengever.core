from ftw.upgrade import UpgradeStep


class AddDebugActionButtons(UpgradeStep):
    """Add debug action buttons.
    """

    def __call__(self):
        self.install_upgrade_profile()
