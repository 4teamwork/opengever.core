from ftw.upgrade import UpgradeStep


class RemoveOCRestAPIFeatureFlag(UpgradeStep):
    """Remove OfficeConnector REST-API feature flag. We now always use the
    REST-API path.
    """

    def __call__(self):
        self.install_upgrade_profile()
