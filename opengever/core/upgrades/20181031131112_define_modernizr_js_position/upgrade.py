from ftw.upgrade import UpgradeStep


class DefineModernizrJsPosition(UpgradeStep):
    """Define modernizr.js position.
    """

    def __call__(self):
        self.install_upgrade_profile()
