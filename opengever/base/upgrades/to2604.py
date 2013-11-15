from ftw.upgrade import UpgradeStep


class InitializeRetentionPeriodRestriction(UpgradeStep):
    """Initialize configurable restricton of the retention_period"""

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2604')
