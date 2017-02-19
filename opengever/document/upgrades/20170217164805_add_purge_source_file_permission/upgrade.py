from ftw.upgrade import UpgradeStep


class AddPurgeSourceFilePermission(UpgradeStep):
    """Add `purge source file` permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
