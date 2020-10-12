from ftw.upgrade import UpgradeStep


class DisableGZipCompressionInPACaching(UpgradeStep):
    """Disable GZip compression in p.a.caching.
    """

    def __call__(self):
        self.install_upgrade_profile()
