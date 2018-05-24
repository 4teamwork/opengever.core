from ftw.upgrade import UpgradeStep


class RegisterUnicodeNormalizerLibrary(UpgradeStep):
    """Register unicode normalizer library.
    """

    def __call__(self):
        self.install_upgrade_profile()
