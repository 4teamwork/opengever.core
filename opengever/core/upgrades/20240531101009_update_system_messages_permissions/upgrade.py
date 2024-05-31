from ftw.upgrade import UpgradeStep


class UpdateSystemMessagesPermissions(UpgradeStep):
    """Update system messages permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
