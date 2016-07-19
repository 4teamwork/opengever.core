from ftw.upgrade import UpgradeStep


class UninstallFtwTooltip(UpgradeStep):
    """Uninstall ftw tooltip.
    """

    def __call__(self):
        self.install_upgrade_profile()
