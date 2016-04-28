from ftw.upgrade import UpgradeStep


class AddRetentionExpirationToWorkflowVariables(UpgradeStep):
    """Add retention_expiration to workflow variables.
    """

    def __call__(self):
        self.install_upgrade_profile()
