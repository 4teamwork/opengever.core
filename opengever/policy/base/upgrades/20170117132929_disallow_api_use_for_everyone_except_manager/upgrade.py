from ftw.upgrade import UpgradeStep


class DisallowAPIUseForEveryoneExceptManager(UpgradeStep):
    """Disallow API use for everyone except Manager.

    (Will be enabled again in a later upgrade for users with the APIUser role)
    """

    def __call__(self):
        self.install_upgrade_profile()
