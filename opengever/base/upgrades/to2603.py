from ftw.upgrade import UpgradeStep


class InitializeReferencenumberFormatter(UpgradeStep):
    """Initalize registry entries for the ReferenceNumber formatters"""

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2603')
