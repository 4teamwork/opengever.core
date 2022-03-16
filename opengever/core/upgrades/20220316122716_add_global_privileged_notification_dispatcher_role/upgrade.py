from ftw.upgrade import UpgradeStep


class AddGlobalPrivilegedNotificationDispatcherRole(UpgradeStep):
    """Add global PrivilegedNotificationDispatcher role.
    """

    def __call__(self):
        self.install_upgrade_profile()
