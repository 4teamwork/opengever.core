from ftw.upgrade import UpgradeStep


class AddResolverNameToIDossierResolveProperties(UpgradeStep):
    """Add resolver_name to IDossierResolveProperties.
    """

    def __call__(self):
        self.install_upgrade_profile()
