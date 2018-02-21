from ftw.upgrade import UpgradeStep


class UpdatePropertiesActionAvailableExpression(UpgradeStep):
    """Update properties action available expression.
    """

    def __call__(self):
        self.install_upgrade_profile()
