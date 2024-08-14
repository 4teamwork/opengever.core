from ftw.upgrade import UpgradeStep


class AddKubDocPropertyAdditionalFields(UpgradeStep):
    """Add kub doc property additional fields.
    """

    def __call__(self):
        self.install_upgrade_profile()
