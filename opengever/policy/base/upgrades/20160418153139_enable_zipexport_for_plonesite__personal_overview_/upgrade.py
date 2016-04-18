from ftw.upgrade import UpgradeStep


class EnableZipexportForPlonesite(UpgradeStep):
    """Enable zipexport for plonesite (personal overview).
    """

    def __call__(self):
        self.install_upgrade_profile()
