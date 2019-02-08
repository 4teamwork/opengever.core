from ftw.upgrade import UpgradeStep


class FixBrokenMimetypes(UpgradeStep):
    """Fix broken mimetypes.
    """

    def __call__(self):
        self.install_upgrade_profile()
