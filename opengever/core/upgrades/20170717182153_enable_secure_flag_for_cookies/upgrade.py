from ftw.upgrade import UpgradeStep
from opengever.core.hooks import enable_secure_flag_for_cookies


class EnableSecureFlagForCookies(UpgradeStep):
    """Enable secure flag for cookies.
    """

    def __call__(self):
        self.install_upgrade_profile()
        enable_secure_flag_for_cookies(self.portal)
