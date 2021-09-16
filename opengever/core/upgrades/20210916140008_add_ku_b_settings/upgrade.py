from ftw.upgrade import UpgradeStep


class AddKuBSettings(UpgradeStep):
    """Add KuB settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
