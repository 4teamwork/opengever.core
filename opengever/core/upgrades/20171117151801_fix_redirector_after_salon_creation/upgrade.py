from ftw.upgrade import UpgradeStep


class FixRedirectorAfterSalonCreation(UpgradeStep):
    """Fix redirector after salon creation.
    """

    def __call__(self):
        self.install_upgrade_profile()
