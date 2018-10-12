from ftw.upgrade import UpgradeStep


class AddARegistryConfigForFutureProofingForAOneoffixxBackendBugEventuallyGettingFixed(UpgradeStep):
    """Add a registry config for future proofing for a Oneoffixx backend bug eventually getting fixed.
    """

    def __call__(self):
        self.install_upgrade_profile()
