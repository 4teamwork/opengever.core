from ftw.upgrade import UpgradeStep


class DefineOverlayhelperOrderInJSRegistry(UpgradeStep):
    """Define overlayhelper order in js registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
