from ftw.upgrade import UpgradeStep


class UninstallFtwTika(UpgradeStep):
    """Uninstall ftw.tika.
    """

    def __call__(self):
        self.uninstall_product('ftw.tika')
