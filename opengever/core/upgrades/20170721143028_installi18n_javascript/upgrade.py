from ftw.upgrade import UpgradeStep


class Installi18nJavascript(UpgradeStep):
    """Installi18n javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
