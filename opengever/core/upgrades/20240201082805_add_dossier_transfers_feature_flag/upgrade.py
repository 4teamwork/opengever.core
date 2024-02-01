from ftw.upgrade import UpgradeStep


class AddDossierTransferFeatureFlag(UpgradeStep):
    """Add dossier transfer feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
