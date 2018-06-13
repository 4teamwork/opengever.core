from ftw.upgrade import UpgradeStep


class ReaddPinJs(UpgradeStep):
    """Readd Pin.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
