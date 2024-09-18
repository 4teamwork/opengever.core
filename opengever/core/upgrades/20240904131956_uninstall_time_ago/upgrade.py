from ftw.upgrade import UpgradeStep


class UninstallTimeAgo(UpgradeStep):
    """Uninstall time ago.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.remove_broken_browserlayer('collective.js.timeago', 'interfaces.ILayer')
