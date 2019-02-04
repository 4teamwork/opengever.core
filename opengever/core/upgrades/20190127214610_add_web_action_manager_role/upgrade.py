from ftw.upgrade import UpgradeStep


class AddWebActionManagerRole(UpgradeStep):
    """Add WebActionManager role to control access to management of WebActions.
    """

    def __call__(self):
        self.install_upgrade_profile()
