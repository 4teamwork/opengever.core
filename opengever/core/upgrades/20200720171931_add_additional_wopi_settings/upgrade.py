from ftw.upgrade import UpgradeStep


class AddAdditionalWOPISettings(UpgradeStep):
    """Add additional wopi settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
