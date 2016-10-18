from ftw.upgrade import UpgradeStep


class ReRegisterPrepoverlayJS(UpgradeStep):
    """Reregister prepoverlay JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
