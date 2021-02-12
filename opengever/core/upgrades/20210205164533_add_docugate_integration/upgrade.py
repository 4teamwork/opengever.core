from ftw.upgrade import UpgradeStep


class AddDocugateIntegration(UpgradeStep):
    """Add docugate integration.
    """

    def __call__(self):
        self.install_upgrade_profile()
