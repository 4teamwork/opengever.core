from ftw.upgrade import UpgradeStep


class AddLinkOptions(UpgradeStep):
    """Add link options.
    """

    def __call__(self):
        self.install_upgrade_profile()
