from ftw.upgrade import UpgradeStep


class AddJSCookie(UpgradeStep):
    """Add js cookie.
    """

    def __call__(self):
        self.install_upgrade_profile()
