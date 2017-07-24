from ftw.upgrade import UpgradeStep


class DisallowReorderingOnRoot_onlyManagersAreWhitelistet(UpgradeStep):
    """Disallow reordering on root, only managers are whitelistet.
    """

    def __call__(self):
        self.install_upgrade_profile()
