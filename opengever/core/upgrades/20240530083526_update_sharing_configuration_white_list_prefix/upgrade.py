from ftw.upgrade import UpgradeStep


class UpdateSharingConfigurationWhiteListPrefix(UpgradeStep):
    """update sharing configuration white list prefix.
    """

    def __call__(self):
        self.install_upgrade_profile()
