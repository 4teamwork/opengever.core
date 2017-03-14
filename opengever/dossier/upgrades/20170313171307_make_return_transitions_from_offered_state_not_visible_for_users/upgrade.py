from ftw.upgrade import UpgradeStep


class MakeReturnTransitionsFromOfferedStateNotVisibleForUsers(UpgradeStep):
    """Make return transitions from offered state not visible for users.
    """

    def __call__(self):
        self.install_upgrade_profile()
